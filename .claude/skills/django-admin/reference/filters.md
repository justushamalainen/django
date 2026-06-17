# Admin Filters Reference

## Custom SimpleListFilter Patterns

### Dynamic Lookups from Database

```python
from django.db.models import Count

class CategoryFilter(admin.SimpleListFilter):
    title = 'category'
    parameter_name = 'cat'

    def lookups(self, request, model_admin):
        # Only categories with products
        categories = Category.objects.annotate(
            product_count=Count('products')
        ).filter(product_count__gt=0)
        return [(c.id, f"{c.name} ({c.product_count})") for c in categories]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category_id=self.value())
```

### Annotation-Based Filter

```python
from django.db.models import Count

class ReviewCountFilter(admin.SimpleListFilter):
    title = 'review count'
    parameter_name = 'reviews'

    def lookups(self, request, model_admin):
        return [('none', 'No reviews'), ('few', '1-5'), ('many', '5+')]

    def queryset(self, request, queryset):
        qs = queryset.annotate(_review_count=Count('reviews'))
        if self.value() == 'none':
            return qs.filter(_review_count=0)
        if self.value() == 'few':
            return qs.filter(_review_count__gte=1, _review_count__lte=5)
        if self.value() == 'many':
            return qs.filter(_review_count__gt=5)
```

### Date-Based with Timezone

```python
from django.utils import timezone
from datetime import timedelta

class RecentActivityFilter(admin.SimpleListFilter):
    title = 'recent activity'
    parameter_name = 'activity'

    def lookups(self, request, model_admin):
        return [('today', 'Today'), ('week', 'Past week'), ('month', 'Past month')]

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

## Advanced Built-in Filters

```python
from django.contrib.admin import RelatedOnlyFieldListFilter, EmptyFieldListFilter

class OrderAdmin(admin.ModelAdmin):
    list_filter = [
        ('customer', RelatedOnlyFieldListFilter),  # Only customers with orders
        ('notes', EmptyFieldListFilter),  # Has/Empty notes
    ]
```

## Optimization Patterns

### Limit Filter Options (Performance)

**GOTCHA: ForeignKey filters load ALL related objects**

```python
class CustomerFilter(admin.SimpleListFilter):
    title = 'top customers'
    parameter_name = 'customer'

    def lookups(self, request, model_admin):
        # Limit to top 50 to avoid loading thousands
        customers = Customer.objects.annotate(
            order_count=Count('orders')
        ).order_by('-order_count')[:50]
        return [(c.id, c.name) for c in customers]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(customer_id=self.value())
```

### Cache Expensive Lookups

```python
from django.core.cache import cache

class CategoryFilter(admin.SimpleListFilter):
    title = 'category'
    parameter_name = 'cat'

    def lookups(self, request, model_admin):
        cache_key = 'admin_category_lookups'
        lookups = cache.get(cache_key)
        if lookups is None:
            categories = Category.objects.filter(active=True)
            lookups = [(c.id, c.name) for c in categories]
            cache.set(cache_key, lookups, 3600)
        return lookups

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category_id=self.value())
```

## Complex Business Logic Filter

```python
from django.utils import timezone

class PublishStatusFilter(admin.SimpleListFilter):
    title = 'publish status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [('published', 'Published'), ('scheduled', 'Scheduled'), ('draft', 'Draft')]

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'published':
            return queryset.filter(status='published', published_date__lte=now)
        if self.value() == 'scheduled':
            return queryset.filter(status='published', published_date__gt=now)
        if self.value() == 'draft':
            return queryset.filter(status='draft')
```
