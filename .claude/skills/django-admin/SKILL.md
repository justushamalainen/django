# Django Admin Skill

Advanced patterns and gotchas for Django admin customization.

## Query Optimization (Critical!)

**GOTCHA: N+1 queries in list_display**

```python
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'total']

    # REQUIRED: Optimize ForeignKey lookups in list_display
    list_select_related = ['customer']

    @admin.display(description='Customer', ordering='customer__name')
    def customer_name(self, obj):
        return obj.customer.name  # No extra query due to list_select_related

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('items')  # For reverse relations
```

## Advanced Patterns

### Custom Display with HTML

```python
from django.utils.html import format_html

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'colored_price', 'stock_status']

    @admin.display(description='Price', ordering='price')
    def colored_price(self, obj):
        color = 'green' if obj.price < 50 else 'red'
        return format_html(
            '<span style="color: {};">${}</span>',
            color, obj.price
        )

    @admin.display(description='Stock', boolean=True)
    def stock_status(self, obj):
        return obj.stock > 0  # boolean=True shows icon
```

### Custom Filter with Dynamic Lookups

```python
from django.contrib import admin
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

### Autocomplete for Large Datasets

**GOTCHA: Raw dropdowns load ALL records**

```python
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']  # MUST use for 1000+ related objects

class CustomerAdmin(admin.ModelAdmin):
    search_fields = ['name', 'email']  # REQUIRED for autocomplete to work
```

## Reference Files

- **reference/modeladmin_options.md**: Quick reference for all ModelAdmin options
- **reference/filters.md**: Built-in and custom filter patterns
- **reference/actions.md**: Complete guide to admin actions

## Related Skills

- **django-models**: Model fields and relationships
- **django-forms**: Custom admin forms
- **django-queries**: Query optimization
- **django-testing**: Testing admin classes
