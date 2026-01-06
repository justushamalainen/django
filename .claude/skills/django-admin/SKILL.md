# Django Admin Skill

## Overview

This skill helps you work with Django's built-in admin interface for quick CRUD operations with minimal code.

**Use this skill when you need to:**
- Create ModelAdmin classes for models
- Configure list displays, filters, and search
- Add custom admin actions (bulk operations)
- Set up inline editing for related models
- Customize admin forms and fieldsets

## When to Use This Skill

**Use django-admin when:**
- Building internal admin interfaces (most Django projects)
- Need quick CRUD interface for staff users
- Managing data through Django's admin site
- Creating bulk operations on querysets

**Consider alternatives when:**
- Building public-facing UIs → Use django-views + django-templates
- Need complex workflows → Use django-forms + custom views
- API-only backends → Use DRF

## Basic ModelAdmin Setup

### Register a Model

```python
from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass
```

Or:

```python
admin.site.register(Product, ProductAdmin)
```

### Essential Display Options

```python
class ProductAdmin(admin.ModelAdmin):
    # Which fields to show in list view
    list_display = ['name', 'price', 'in_stock', 'category']

    # Make fields editable in list view
    list_editable = ['price', 'in_stock']

    # Enable search box
    search_fields = ['name', 'sku', 'description']

    # Add filters to sidebar
    list_filter = ['in_stock', 'category', 'created_at']

    # Default ordering
    ordering = ['-created_at']

    # Date drill-down navigation
    date_hierarchy = 'created_at'

    # Items per page
    list_per_page = 50
```

### Form Configuration

```python
class ProductAdmin(admin.ModelAdmin):
    # Organize fields into sections
    fieldsets = [
        ('Basic Info', {
            'fields': ['name', 'sku', 'price']
        }),
        ('Details', {
            'fields': ['description', 'category', 'tags'],
            'classes': ['collapse']  # Collapsed by default
        }),
    ]

    # Or simple field list
    fields = ['name', 'sku', 'price', 'description']

    # Auto-populate slug from title
    prepopulated_fields = {'slug': ['name']}

    # Use autocomplete for foreign keys
    autocomplete_fields = ['category']

    # Better widget for many-to-many
    filter_horizontal = ['tags']

    # Read-only fields
    readonly_fields = ['created_at', 'updated_at']
```

## Custom Admin Actions

Actions allow bulk operations on selected items.

### Basic Action

```python
from django.contrib import admin

@admin.action(description="Mark selected as published")
def make_published(modeladmin, request, queryset):
    updated = queryset.update(status='published')
    modeladmin.message_user(request, f"{updated} items published.")

class ArticleAdmin(admin.ModelAdmin):
    actions = [make_published]
```

### Action with Validation

```python
from django.contrib import messages

@admin.action(description="Archive selected items")
def archive_items(modeladmin, request, queryset):
    if queryset.count() > 100:
        modeladmin.message_user(
            request,
            "Cannot archive more than 100 items at once.",
            level=messages.ERROR
        )
        return

    queryset.update(archived=True)
    modeladmin.message_user(request, f"Archived {queryset.count()} items.")
```

### Export Action

```python
import csv
from django.http import HttpResponse

@admin.action(description="Export to CSV")
def export_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Email'])

    for obj in queryset:
        writer.writerow([obj.id, obj.name, obj.email])

    return response
```

## Inline Editing

Edit related models on the same page.

```python
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Number of empty forms
    fields = ['product', 'quantity', 'price']
    autocomplete_fields = ['product']

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ['id', 'customer', 'total', 'status']
```

## Query Optimization

Avoid N+1 queries with select_related and prefetch_related.

```python
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'total']

    # Optimize ForeignKey lookups in list_display
    list_select_related = ['customer']

    @admin.display(description='Customer')
    def customer_name(self, obj):
        return obj.customer.name  # No extra query

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Optimize reverse relations
        return qs.prefetch_related('items')
```

## Common Patterns

### Custom Display Methods

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
        return obj.stock > 0
```

### Custom Filters

```python
from django.contrib import admin

class PriceRangeFilter(admin.SimpleListFilter):
    title = 'price range'
    parameter_name = 'price'

    def lookups(self, request, model_admin):
        return [
            ('0-50', 'Under $50'),
            ('50-100', '$50-$100'),
            ('100+', 'Over $100'),
        ]

    def queryset(self, request, queryset):
        if self.value() == '0-50':
            return queryset.filter(price__lt=50)
        if self.value() == '50-100':
            return queryset.filter(price__gte=50, price__lt=100)
        if self.value() == '100+':
            return queryset.filter(price__gte=100)

class ProductAdmin(admin.ModelAdmin):
    list_filter = [PriceRangeFilter, 'category']
```

## Best Practices

### ✓ DO: Optimize Queries
```python
class ProductAdmin(admin.ModelAdmin):
    list_select_related = ['category']  # For ForeignKey

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('images')  # For reverse relations
```

### ✓ DO: Use Autocomplete for Large Datasets
```python
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']  # Instead of raw dropdown

class CustomerAdmin(admin.ModelAdmin):
    search_fields = ['name', 'email']  # Required for autocomplete
```

### ✗ DON'T: Display Uncached Related Fields
```python
# Bad: N+1 queries
list_display = ['name', 'category_name']
def category_name(self, obj):
    return obj.category.name  # Extra query per row!

# Good: Use list_select_related
list_display = ['name', 'category_name']
list_select_related = ['category']
@admin.display(description='Category', ordering='category__name')
def category_name(self, obj):
    return obj.category.name  # No extra query
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
