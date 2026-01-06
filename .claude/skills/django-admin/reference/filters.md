# Admin Filters Reference

Guide to using built-in and custom filters in Django admin.

## Built-in Filters

### Basic Field Filters

Django automatically creates filters based on field type:

```python
class ProductAdmin(admin.ModelAdmin):
    list_filter = [
        'in_stock',      # BooleanField → Yes/No/All
        'category',      # ForeignKey → All category values
        'status',        # CharField with choices → Choice values
        'created_at',    # DateField → Date ranges (Today, Past 7 days, etc.)
    ]
```

### Boolean Field Filter

```python
class ProductAdmin(admin.ModelAdmin):
    list_filter = ['in_stock', 'featured']

# Sidebar shows:
# - All
# - Yes
# - No
```

### ForeignKey Filter

```python
class ProductAdmin(admin.ModelAdmin):
    list_filter = ['category']

# Shows all categories in sidebar
# Can be slow with many related objects
```

### Date Field Filter

```python
class ArticleAdmin(admin.ModelAdmin):
    list_filter = ['published_date']

# Automatic ranges:
# - Any date
# - Today
# - Past 7 days
# - This month
# - This year
```

### Choice Field Filter

```python
class Product(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

class ProductAdmin(admin.ModelAdmin):
    list_filter = ['status']

# Shows all status choices
```

### Related Field Filters

Filter by related object's fields:

```python
class OrderAdmin(admin.ModelAdmin):
    list_filter = [
        'customer__city',           # Customer's city
        'items__product__category', # Product category via items
    ]
```

## Custom SimpleListFilter

Create custom filter logic with any criteria.

### Basic Custom Filter

```python
from django.contrib import admin

class PriceRangeFilter(admin.SimpleListFilter):
    title = 'price range'        # Filter title in sidebar
    parameter_name = 'price'      # URL parameter name

    def lookups(self, request, model_admin):
        """Return list of (value, label) tuples"""
        return [
            ('0-50', 'Under $50'),
            ('50-100', '$50 - $100'),
            ('100+', 'Over $100'),
        ]

    def queryset(self, request, queryset):
        """Return filtered queryset based on value"""
        if self.value() == '0-50':
            return queryset.filter(price__lt=50)
        if self.value() == '50-100':
            return queryset.filter(price__gte=50, price__lt=100)
        if self.value() == '100+':
            return queryset.filter(price__gte=100)

class ProductAdmin(admin.ModelAdmin):
    list_filter = [PriceRangeFilter, 'category']
```

### Dynamic Lookups

Generate filter options from database:

```python
from django.db.models import Count

class CategoryFilter(admin.SimpleListFilter):
    title = 'category'
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        # Only show categories with products
        categories = Category.objects.annotate(
            product_count=Count('products')
        ).filter(product_count__gt=0)

        return [
            (cat.id, f"{cat.name} ({cat.product_count})")
            for cat in categories
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category_id=self.value())
```

### Date-Based Filter

```python
from django.utils import timezone
from datetime import timedelta

class RecentActivityFilter(admin.SimpleListFilter):
    title = 'recent activity'
    parameter_name = 'activity'

    def lookups(self, request, model_admin):
        return [
            ('today', 'Today'),
            ('week', 'Past week'),
            ('month', 'Past month'),
        ]

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'today':
            start = now.replace(hour=0, minute=0, second=0)
            return queryset.filter(updated_at__gte=start)
        if self.value() == 'week':
            return queryset.filter(updated_at__gte=now - timedelta(days=7))
        if self.value() == 'month':
            return queryset.filter(updated_at__gte=now - timedelta(days=30))
```

### Null/Empty Filter

```python
class HasDescriptionFilter(admin.SimpleListFilter):
    title = 'has description'
    parameter_name = 'has_desc'

    def lookups(self, request, model_admin):
        return [
            ('yes', 'Has description'),
            ('no', 'No description'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(description='').exclude(description__isnull=True)
        if self.value() == 'no':
            return queryset.filter(
                models.Q(description='') | models.Q(description__isnull=True)
            )
```

### Annotation-Based Filter

Filter by computed values:

```python
from django.db.models import Count

class ReviewCountFilter(admin.SimpleListFilter):
    title = 'review count'
    parameter_name = 'reviews'

    def lookups(self, request, model_admin):
        return [
            ('none', 'No reviews'),
            ('few', '1-5 reviews'),
            ('many', '5+ reviews'),
        ]

    def queryset(self, request, queryset):
        queryset = queryset.annotate(_review_count=Count('reviews'))

        if self.value() == 'none':
            return queryset.filter(_review_count=0)
        if self.value() == 'few':
            return queryset.filter(_review_count__gte=1, _review_count__lte=5)
        if self.value() == 'many':
            return queryset.filter(_review_count__gt=5)
```

## Advanced Built-in Filters

### Related Objects Only

Show only related objects that exist:

```python
from django.contrib.admin import RelatedOnlyFieldListFilter

class OrderAdmin(admin.ModelAdmin):
    list_filter = [
        ('customer', RelatedOnlyFieldListFilter),  # Only customers with orders
    ]
```

### Empty Field Filter

Filter for empty/non-empty values:

```python
from django.contrib.admin import EmptyFieldListFilter

class ProductAdmin(admin.ModelAdmin):
    list_filter = [
        ('description', EmptyFieldListFilter),  # Has/Empty description
    ]
```

### All Values Filter

Show all possible values for a field:

```python
from django.contrib.admin import AllValuesFieldListFilter

class ProductAdmin(admin.ModelAdmin):
    list_filter = [
        ('manufacturer', AllValuesFieldListFilter),  # All manufacturers
    ]
```

## Best Practices

### 1. Optimize Filter Queries

Use select_related for ForeignKey filters:

```python
class OrderAdmin(admin.ModelAdmin):
    list_filter = ['customer', 'status']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('customer')
```

### 2. Limit Filter Options

Prevent thousands of filter options:

```python
class CustomerFilter(admin.SimpleListFilter):
    title = 'top customers'
    parameter_name = 'customer'

    def lookups(self, request, model_admin):
        # Only show top 50 customers
        customers = Customer.objects.annotate(
            order_count=Count('orders')
        ).order_by('-order_count')[:50]

        return [(c.id, c.name) for c in customers]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(customer_id=self.value())
```

### 3. Use Descriptive Labels

```python
class StockFilter(admin.SimpleListFilter):
    title = 'stock status'
    parameter_name = 'stock'

    def lookups(self, request, model_admin):
        return [
            ('in', 'In Stock (10+)'),        # Clear labels
            ('low', 'Low Stock (1-9)'),
            ('out', 'Out of Stock'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'in':
            return queryset.filter(stock__gte=10)
        if self.value() == 'low':
            return queryset.filter(stock__gt=0, stock__lt=10)
        if self.value() == 'out':
            return queryset.filter(stock=0)
```

### 4. Cache Expensive Lookups

```python
from django.core.cache import cache

class CategoryFilter(admin.SimpleListFilter):
    title = 'category'
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        cache_key = 'admin_category_lookups'
        lookups = cache.get(cache_key)

        if lookups is None:
            categories = Category.objects.filter(active=True)
            lookups = [(c.id, c.name) for c in categories]
            cache.set(cache_key, lookups, 3600)  # 1 hour

        return lookups

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category_id=self.value())
```

## Complete Examples

### E-commerce Product Filters

```python
class StockLevelFilter(admin.SimpleListFilter):
    title = 'stock level'
    parameter_name = 'stock'

    def lookups(self, request, model_admin):
        return [
            ('in_stock', 'In Stock'),
            ('low', 'Low Stock (< 10)'),
            ('out', 'Out of Stock'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'in_stock':
            return queryset.filter(stock__gte=10)
        if self.value() == 'low':
            return queryset.filter(stock__gt=0, stock__lt=10)
        if self.value() == 'out':
            return queryset.filter(stock=0)

class ProductAdmin(admin.ModelAdmin):
    list_filter = [
        StockLevelFilter,
        'category',
        'in_stock',
        'created_at',
    ]
```

### Blog Article Filters

```python
from django.utils import timezone

class PublishStatusFilter(admin.SimpleListFilter):
    title = 'publish status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [
            ('published', 'Published'),
            ('scheduled', 'Scheduled'),
            ('draft', 'Draft'),
        ]

    def queryset(self, request, queryset):
        now = timezone.now()

        if self.value() == 'published':
            return queryset.filter(
                status='published',
                published_date__lte=now
            )
        if self.value() == 'scheduled':
            return queryset.filter(
                status='published',
                published_date__gt=now
            )
        if self.value() == 'draft':
            return queryset.filter(status='draft')

class ArticleAdmin(admin.ModelAdmin):
    list_filter = [
        PublishStatusFilter,
        'category',
        'featured',
        'published_date',
    ]
```

## Troubleshooting

### Too Many Filter Options

**Problem**: ForeignKey filter shows thousands of items.

**Solution**: Use custom filter with limited lookups or autocomplete search instead.

### Slow Filter Performance

**Problem**: Filter query takes too long.

**Solution**:
- Add database indexes on filtered fields
- Use `select_related()` in `get_queryset()`
- Cache filter lookups

### Filter Not Applied

**Problem**: Filter selected but queryset unchanged.

**Solution**: Check that `parameter_name` in `lookups()` matches `self.value()` check in `queryset()`.

## Tips

1. Use built-in filters when possible (simpler, maintained by Django)
2. Create custom filters for business logic (price ranges, status combinations)
3. Limit filter options to keep UI manageable (< 100 items)
4. Use clear, descriptive labels for filter options
5. Optimize filter queries with select_related/prefetch_related
6. Cache expensive filter lookups
7. Test filters with edge cases (null values, empty querysets)

For more details, see Django documentation: https://docs.djangoproject.com/en/stable/ref/contrib/admin/filters/
