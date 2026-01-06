# ModelAdmin Options Reference

Quick reference for commonly used Django ModelAdmin configuration options.

## Essential Options Table

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

Use prefixes in `search_fields` to control search behavior:

- No prefix: `'name'` → Contains (case-insensitive)
- `^`: `'^name'` → Starts with
- `=`: `'=id'` → Exact match
- `@`: `'@description'` → Full-text search (PostgreSQL)

Example:
```python
search_fields = ['name', '^sku', '=id', 'category__name']
```

## Display Method Decorator

Use `@admin.display` to customize display methods:

```python
@admin.display(description='Total Price', ordering='price', boolean=False, empty_value='N/A')
def total_price(self, obj):
    return f"${obj.price}"
```

**Decorator parameters:**
- `description`: Column header text
- `ordering`: Field(s) for sorting
- `boolean`: Display as boolean icon
- `empty_value`: Text for None values

## Fieldsets Structure

```python
fieldsets = [
    ('Section Title', {
        'fields': ['field1', ('field2', 'field3')],  # Tuples = same row
        'classes': ['collapse', 'wide'],  # CSS classes
        'description': 'Help text for this section',
    }),
]
```

**Common classes:**
- `collapse`: Collapsed by default
- `wide`: Extra wide
- `extrapretty`: Extra styling

## Inline Options

```python
class ItemInline(admin.TabularInline):  # or StackedInline
    model = OrderItem
    extra = 1              # Empty forms to show
    max_num = 10           # Maximum forms
    min_num = 1            # Minimum required
    can_delete = True      # Show delete checkbox
    show_change_link = True  # Link to full edit
    fields = ['product', 'qty', 'price']
    readonly_fields = ['total']
    autocomplete_fields = ['product']
    ordering = ['position']
```

## Common Methods

### get_queryset()
Customize the base queryset for optimization or filtering:

```python
def get_queryset(self, request):
    qs = super().get_queryset(request)
    qs = qs.select_related('category')  # Optimize
    qs = qs.prefetch_related('tags')
    if not request.user.is_superuser:
        qs = qs.filter(owner=request.user)  # Filter
    return qs
```

### get_readonly_fields()
Dynamic readonly fields based on context:

```python
def get_readonly_fields(self, request, obj=None):
    if obj and obj.status == 'published':
        return ['title', 'content']
    return []
```

### save_model()
Hook into save process:

```python
def save_model(self, request, obj, form, change):
    if not change:  # New object
        obj.created_by = request.user
    obj.modified_by = request.user
    super().save_model(request, obj, form, change)
```

## Permission Methods

Control access at model and object level:

```python
def has_add_permission(self, request):
    return request.user.is_superuser

def has_change_permission(self, request, obj=None):
    if obj is None:
        return True  # List view
    return obj.owner == request.user  # Object level

def has_delete_permission(self, request, obj=None):
    return request.user.is_superuser

def has_view_permission(self, request, obj=None):
    return True  # Everyone can view
```

## Complete Example

```python
from django.contrib import admin
from django.db.models import Count

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text']

@admin.action(description="Mark as featured")
def make_featured(modeladmin, request, queryset):
    queryset.update(featured=True)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Display
    list_display = ['name', 'price', 'in_stock', 'review_count']
    list_editable = ['price', 'in_stock']
    list_per_page = 50
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    # Search & Filter
    search_fields = ['name', 'sku', 'category__name']
    list_filter = ['in_stock', 'category', 'created_at']

    # Form
    fieldsets = [
        ('Basic', {'fields': ['name', 'sku', 'price']}),
        ('Details', {'fields': ['description', 'category', 'tags']}),
    ]
    autocomplete_fields = ['category']
    filter_horizontal = ['tags']
    prepopulated_fields = {'slug': ['name']}
    readonly_fields = ['created_at']

    # Optimization
    list_select_related = ['category']

    # Actions & Inlines
    actions = [make_featured]
    inlines = [ProductImageInline]
    save_on_top = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_review_count=Count('reviews'))

    @admin.display(description='Reviews', ordering='_review_count')
    def review_count(self, obj):
        return obj._review_count
```

## Tips

1. **Performance**: Always use `list_select_related` for ForeignKey fields in `list_display`
2. **Large Datasets**: Use `autocomplete_fields` instead of raw dropdown for relations
3. **User Experience**: Use `filter_horizontal` for ManyToMany fields (better than default)
4. **Readonly**: Use `readonly_fields` for computed values or system fields
5. **Organization**: Use `fieldsets` for complex forms, `fields` for simple ones

For more details, see Django documentation: https://docs.djangoproject.com/en/stable/ref/contrib/admin/
