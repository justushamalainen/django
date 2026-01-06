# Admin Actions Reference

Guide to creating custom bulk operations in Django admin.

## Basic Actions

### Simple Action Function

Basic action that updates selected items:

```python
from django.contrib import admin

def make_published(modeladmin, request, queryset):
    """Mark selected items as published"""
    updated = queryset.update(status='published')
    modeladmin.message_user(request, f"{updated} items marked as published.")

class ArticleAdmin(admin.ModelAdmin):
    actions = [make_published]
```

### Action as Method

Define action as ModelAdmin method:

```python
class ArticleAdmin(admin.ModelAdmin):
    actions = ['make_published', 'make_draft']

    def make_published(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f"{updated} items published.")

    def make_draft(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f"{updated} items marked as draft.")
```

## Action Decorator

Use `@admin.action` decorator (Django 3.2+) for cleaner configuration:

```python
from django.contrib import admin

@admin.action(description="Mark selected items as published")
def make_published(modeladmin, request, queryset):
    updated = queryset.update(status='published')
    modeladmin.message_user(request, f"{updated} items published.")

class ArticleAdmin(admin.ModelAdmin):
    actions = [make_published]
```

### Action with Permissions

Restrict action to users with specific permissions:

```python
@admin.action(
    description="Delete selected items permanently",
    permissions=['delete']
)
def permanent_delete(modeladmin, request, queryset):
    queryset.delete()
    modeladmin.message_user(request, "Items deleted permanently.")

class ArticleAdmin(admin.ModelAdmin):
    actions = [permanent_delete]

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
```

### Custom Permission Check

```python
@admin.action(
    description="Export to CSV",
    permissions=['export']
)
def export_csv(modeladmin, request, queryset):
    # Export logic
    pass

class ArticleAdmin(admin.ModelAdmin):
    actions = [export_csv]

    def has_export_permission(self, request):
        return request.user.groups.filter(name='Exporters').exists()
```

## Common Action Patterns

### Export to CSV

```python
import csv
from django.http import HttpResponse

@admin.action(description="Export to CSV")
def export_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Email', 'Created'])

    for obj in queryset:
        writer.writerow([
            obj.id,
            obj.name,
            obj.email,
            obj.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    return response

class UserAdmin(admin.ModelAdmin):
    actions = [export_csv]
```

### Action with Validation

```python
from django.contrib import messages

@admin.action(description="Archive selected items")
def archive_items(modeladmin, request, queryset):
    count = queryset.count()

    if count > 100:
        modeladmin.message_user(
            request,
            f"Cannot archive {count} items at once. Limit is 100.",
            level=messages.ERROR
        )
        return

    queryset.update(archived=True)
    modeladmin.message_user(
        request,
        f"Successfully archived {count} items.",
        level=messages.SUCCESS
    )
```

### Action with Error Handling

```python
from django.db import transaction

@admin.action(description="Bulk process items")
def bulk_process(modeladmin, request, queryset):
    success_count = 0
    error_count = 0
    errors = []

    for item in queryset:
        try:
            with transaction.atomic():
                item.process()
                success_count += 1
        except Exception as e:
            error_count += 1
            errors.append(f"{item}: {str(e)}")

    if success_count:
        modeladmin.message_user(
            request,
            f"Successfully processed {success_count} items.",
            level=messages.SUCCESS
        )

    if error_count:
        error_message = f"Failed to process {error_count} items: "
        error_message += ", ".join(errors[:3])
        if len(errors) > 3:
            error_message += f" and {len(errors) - 3} more"

        modeladmin.message_user(
            request,
            error_message,
            level=messages.ERROR
        )
```

### Clone Objects

```python
@admin.action(description="Clone selected items")
def clone_items(modeladmin, request, queryset):
    cloned = 0
    for obj in queryset:
        obj.pk = None  # Create new object
        obj.name = f"{obj.name} (Copy)"
        obj.save()
        cloned += 1

    modeladmin.message_user(
        request,
        f"Cloned {cloned} items."
    )
```

## Actions with Confirmation

Show confirmation page before executing:

```python
from django.shortcuts import render

@admin.action(description="Bulk delete selected items")
def bulk_delete(modeladmin, request, queryset):
    # POST means user confirmed
    if request.POST.get('post'):
        count = queryset.count()
        queryset.delete()
        modeladmin.message_user(
            request,
            f"Successfully deleted {count} items."
        )
        return

    # Show confirmation page
    context = {
        'title': 'Confirm bulk deletion',
        'queryset': queryset,
        'action': 'bulk_delete',
        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
    }
    return render(request, 'admin/bulk_delete_confirmation.html', context)

class ArticleAdmin(admin.ModelAdmin):
    actions = [bulk_delete]
```

**Template (admin/bulk_delete_confirmation.html):**

```html
{% extends "admin/base_site.html" %}

{% block content %}
<form method="post">
  {% csrf_token %}

  <p>Are you sure you want to delete {{ queryset.count }} items?</p>

  <ul>
    {% for obj in queryset %}
    <li>{{ obj }}</li>
    {% endfor %}
  </ul>

  {% for obj in queryset %}
  <input type="hidden" name="{{ action_checkbox_name }}" value="{{ obj.pk }}" />
  {% endfor %}

  <input type="hidden" name="action" value="{{ action }}" />
  <input type="hidden" name="post" value="yes" />

  <input type="submit" value="Yes, delete" />
  <a href="../">Cancel</a>
</form>
{% endblock %}
```

## Actions with Forms

Collect additional input before processing:

```python
from decimal import Decimal

from django import forms
from django.db import transaction
from django.db.models import DecimalField, F
from django.db.models.expressions import ExpressionWrapper
from django.shortcuts import render, redirect
from django.urls import path

class BulkPriceUpdateForm(forms.Form):
    price_adjustment = forms.DecimalField(
        label="Price Adjustment (%)",
        help_text="Enter percentage (e.g., 10 for +10%, -5 for -5%)"
    )

class ProductAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'bulk-price-update/',
                self.admin_site.admin_view(self.bulk_price_update_view),
                name='products_product_bulk_price_update'
            ),
        ]
        return custom_urls + urls

    @admin.action(description="Bulk update prices")
    def bulk_update_prices(self, request, queryset):
        # Store selected IDs in session
        request.session['bulk_price_update_ids'] = list(
            queryset.values_list('pk', flat=True)
        )
        return redirect('admin:products_product_bulk_price_update')

    def bulk_price_update_view(self, request):
        product_ids = request.session.get('bulk_price_update_ids', [])
        product_count = Product.objects.filter(pk__in=product_ids).count()

        if request.method == 'POST':
            form = BulkPriceUpdateForm(request.POST)
            if form.is_valid():
                adjustment = form.cleaned_data['price_adjustment']
                multiplier = Decimal('1') + Decimal(adjustment) / Decimal('100')

                # Single atomic update instead of N+1 saves
                with transaction.atomic():
                    Product.objects.filter(pk__in=product_ids).update(
                        price=ExpressionWrapper(
                            F('price') * multiplier,
                            output_field=DecimalField()
                        )
                    )

                self.message_user(
                    request,
                    f"Updated prices for {product_count} products."
                )
                del request.session['bulk_price_update_ids']
                return redirect('..')
        else:
            form = BulkPriceUpdateForm()

        context = {
            **self.admin_site.each_context(request),
            'title': 'Bulk Price Update',
            'form': form,
            'products': Product.objects.filter(pk__in=product_ids),
        }
        return render(request, 'admin/bulk_price_update.html', context)

    actions = [bulk_update_prices]
```

## Best Practices

### 1. Always Provide Feedback

```python
@admin.action(description="Process items")
def process_items(modeladmin, request, queryset):
    count = queryset.count()
    queryset.update(processed=True)

    # Always tell user what happened
    modeladmin.message_user(
        request,
        f"Successfully processed {count} items."
    )
```

### 2. Handle Empty Querysets

```python
@admin.action(description="Process items")
def process_items(modeladmin, request, queryset):
    if not queryset.exists():
        modeladmin.message_user(
            request,
            "No items selected.",
            level=messages.WARNING
        )
        return

    # Process...
```

### 3. Use Transactions

```python
from django.db import transaction

@admin.action(description="Bulk update")
def bulk_update(modeladmin, request, queryset):
    with transaction.atomic():
        for obj in queryset:
            obj.process()
            obj.save()

    modeladmin.message_user(request, "Update complete.")
```

### 4. Optimize Queries

```python
@admin.action(description="Process with relations")
def process_with_relations(modeladmin, request, queryset):
    # Bad: N+1 queries
    # for obj in queryset:
    #     print(obj.category.name)

    # Good: Optimize with select_related
    queryset = queryset.select_related('category')
    for obj in queryset:
        print(obj.category.name)
```

### 5. Validate Permissions

```python
@admin.action(description="Delete items", permissions=['delete'])
def delete_items(modeladmin, request, queryset):
    # Permission automatically checked by decorator
    queryset.delete()

class ArticleAdmin(admin.ModelAdmin):
    actions = [delete_items]

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
```

## Complete Examples

### Blog Article Actions

```python
from django.utils import timezone

@admin.action(description="Publish selected articles")
def publish_articles(modeladmin, request, queryset):
    queryset = queryset.filter(status='draft')
    updated = queryset.update(
        status='published',
        published_at=timezone.now()
    )
    modeladmin.message_user(
        request,
        f"Published {updated} articles."
    )

@admin.action(description="Schedule for tomorrow")
def schedule_tomorrow(modeladmin, request, queryset):
    tomorrow = timezone.now() + timezone.timedelta(days=1)
    tomorrow = tomorrow.replace(hour=9, minute=0, second=0)

    updated = queryset.update(
        status='scheduled',
        published_at=tomorrow
    )
    modeladmin.message_user(
        request,
        f"Scheduled {updated} articles for {tomorrow}."
    )

@admin.action(description="Feature on homepage", permissions=['change'])
def feature_articles(modeladmin, request, queryset):
    # Unfeature all current
    Article.objects.filter(featured=True).update(featured=False)

    # Feature selected
    updated = queryset.update(featured=True)
    modeladmin.message_user(
        request,
        f"Featured {updated} articles."
    )

class ArticleAdmin(admin.ModelAdmin):
    actions = [publish_articles, schedule_tomorrow, feature_articles]
    list_display = ['title', 'status', 'published_at', 'featured']
    list_filter = ['status', 'featured']
```

### E-commerce Product Actions

```python
from decimal import Decimal

@admin.action(description="Apply 10% discount")
def apply_discount(modeladmin, request, queryset):
    for product in queryset:
        product.price *= Decimal('0.9')
        product.save()

    modeladmin.message_user(
        request,
        f"Applied discount to {queryset.count()} products."
    )

@admin.action(description="Mark as out of stock")
def mark_out_of_stock(modeladmin, request, queryset):
    updated = queryset.update(in_stock=False, stock=0)
    modeladmin.message_user(
        request,
        f"Marked {updated} products as out of stock."
    )

@admin.action(description="Clone products")
def clone_products(modeladmin, request, queryset):
    cloned = 0
    for product in queryset:
        product.pk = None
        product.name = f"{product.name} (Copy)"
        product.sku = f"{product.sku}-COPY"
        product.save()
        cloned += 1

    modeladmin.message_user(
        request,
        f"Cloned {cloned} products."
    )

class ProductAdmin(admin.ModelAdmin):
    actions = [apply_discount, mark_out_of_stock, clone_products]
```

## Troubleshooting

### Action Not Appearing

**Problem**: Action doesn't show in admin.

**Solution**:
- Check action is in `actions` list
- Verify user has required permissions
- Ensure action is correctly defined

### Action Does Nothing

**Problem**: Action executes but no changes.

**Solution**:
- Check queryset is not empty
- Verify update/save is called
- Look for silent exceptions

### Permission Denied

**Problem**: Action grayed out or not visible.

**Solution**:
- User needs required permission
- Permission check method must exist (`has_{permission}_permission`)
- Permission name must match decorator

## Tips

1. **Always provide user feedback** with `message_user()`
2. **Handle errors gracefully** with try/except blocks
3. **Use transactions** for data integrity
4. **Optimize queries** with select_related/prefetch_related
5. **Check permissions** appropriately
6. **Validate input** before processing
7. **Test edge cases** (empty queryset, errors, permissions)

For more details, see Django documentation: https://docs.djangoproject.com/en/stable/ref/contrib/admin/actions/
