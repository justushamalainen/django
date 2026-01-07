# ModelAdmin Options Reference

## Essential Options

| Option | Purpose | Example |
|--------|---------|---------|
| **Display Options** |
| `list_display` | Columns in list view | `['name', 'price', 'status']` |
| `list_display_links` | Clickable fields | `['name', 'sku']` |
| `list_editable` | Edit in list view | `['price', 'in_stock']` |
| `list_per_page` | Pagination size | `50` |
| `ordering` | Default sort | `['-created_at']` |
| `date_hierarchy` | Date drill-down | `'published_date'` |
| `empty_value_display` | Text for None | `'-empty-'` |
| **Search & Filter** |
| `search_fields` | Enable search | `['name', 'sku', 'category__name']` |
| `list_filter` | Sidebar filters | `['status', 'category', 'created_at']` |
| **Form Options** |
| `fields` | Simple field list | `['name', 'price', 'description']` |
| `fieldsets` | Grouped fields | `[('Info', {'fields': [...]})]` |
| `readonly_fields` | Non-editable | `['created_at', 'id']` |
| `prepopulated_fields` | Auto-fill | `{'slug': ['title']}` |
| `autocomplete_fields` | Autocomplete widget | `['category', 'author']` |
| `filter_horizontal` | M2M widget | `['tags']` |
| `filter_vertical` | M2M widget (vertical) | `['categories']` |
| `raw_id_fields` | ID input widget | `['customer']` |
| **Optimization** |
| `list_select_related` | Optimize FK | `['category', 'author']` |
| **Actions & Inlines** |
| `actions` | Bulk operations | `[publish, archive]` |
| `inlines` | Related models | `[ItemInline]` |
| **Misc** |
| `save_on_top` | Top save buttons | `True` |
| `save_as` | "Save as new" button | `True` |
| `view_on_site` | "View on site" link | `True` |

## Search Field Prefixes

```python
search_fields = ['name', '^sku', '=id', '@description', 'category__name']
# No prefix = contains, ^ = starts with, = = exact, @ = full-text (PostgreSQL)
```

## Key Overrides

```python
class ProductAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('category').prefetch_related('tags')
        if not request.user.is_superuser:
            qs = qs.filter(owner=request.user)  # Object-level filtering
        return qs

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == 'published':
            return ['title', 'content']  # Dynamic based on state
        return []

    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True  # List view
        return obj.owner == request.user  # Object-level permission
```

## Complete Example with Annotations

```python
from django.contrib import admin
from django.db.models import Count

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'in_stock', 'review_count']
    list_editable = ['price', 'in_stock']
    search_fields = ['name', '^sku', 'category__name']
    list_filter = ['in_stock', 'category']
    autocomplete_fields = ['category']
    filter_horizontal = ['tags']
    prepopulated_fields = {'slug': ['name']}

    # CRITICAL: Optimize ForeignKey in list_display
    list_select_related = ['category']

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_review_count=Count('reviews'))

    @admin.display(description='Reviews', ordering='_review_count')
    def review_count(self, obj):
        return obj._review_count  # Uses annotation
```
