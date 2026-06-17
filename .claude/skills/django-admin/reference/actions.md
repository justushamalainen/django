# Admin Actions Reference

Advanced patterns for custom bulk operations in Django admin.

## Action with Error Handling

```python
from django.db import transaction
from django.contrib import messages

@admin.action(description="Bulk process items")
def bulk_process(modeladmin, request, queryset):
    success_count = 0
    errors = []

    for item in queryset:
        try:
            with transaction.atomic():
                item.process()
                success_count += 1
        except Exception as e:
            errors.append(f"{item}: {str(e)}")

    if success_count:
        modeladmin.message_user(request, f"Processed {success_count} items.", messages.SUCCESS)

    if errors:
        error_msg = f"Failed {len(errors)}: " + ", ".join(errors[:3])
        if len(errors) > 3:
            error_msg += f" and {len(errors) - 3} more"
        modeladmin.message_user(request, error_msg, messages.ERROR)
```

## Action with Confirmation Page

```python
from django.shortcuts import render
from django.contrib import admin

@admin.action(description="Bulk delete selected items")
def bulk_delete(modeladmin, request, queryset):
    if request.POST.get('post'):  # User confirmed
        count = queryset.count()
        queryset.delete()
        modeladmin.message_user(request, f"Deleted {count} items.")
        return

    # Show confirmation
    context = {
        'title': 'Confirm bulk deletion',
        'queryset': queryset,
        'action': 'bulk_delete',
        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
    }
    return render(request, 'admin/bulk_delete_confirmation.html', context)
```

**Template (admin/bulk_delete_confirmation.html):**

```html
{% extends "admin/base_site.html" %}
{% block content %}
<form method="post">
  {% csrf_token %}
  <p>Delete {{ queryset.count }} items?</p>
  <ul>{% for obj in queryset %}<li>{{ obj }}</li>{% endfor %}</ul>
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

## Action with Form (Intermediate Page)

**Pattern for collecting additional input before processing:**

```python
from decimal import Decimal
from django import forms
from django.db import transaction
from django.db.models import DecimalField, F, ExpressionWrapper
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import admin

class BulkPriceUpdateForm(forms.Form):
    price_adjustment = forms.DecimalField(
        label="Price Adjustment (%)",
        help_text="Enter percentage (e.g., 10 for +10%, -5 for -5%)"
    )

class ProductAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-price-update/',
                 self.admin_site.admin_view(self.bulk_price_update_view),
                 name='products_product_bulk_price_update'),
        ]
        return custom_urls + urls

    @admin.action(description="Bulk update prices")
    def bulk_update_prices(self, request, queryset):
        # Store selected IDs in session
        request.session['bulk_price_update_ids'] = list(queryset.values_list('pk', flat=True))
        return redirect('admin:products_product_bulk_price_update')

    def bulk_price_update_view(self, request):
        product_ids = request.session.get('bulk_price_update_ids', [])

        if request.method == 'POST':
            form = BulkPriceUpdateForm(request.POST)
            if form.is_valid():
                adjustment = form.cleaned_data['price_adjustment']
                multiplier = Decimal('1') + adjustment / Decimal('100')

                # CRITICAL: Single atomic update, not N+1 saves
                with transaction.atomic():
                    Product.objects.filter(pk__in=product_ids).update(
                        price=ExpressionWrapper(F('price') * multiplier, output_field=DecimalField())
                    )

                self.message_user(request, f"Updated {len(product_ids)} products.")
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

## Permission-Based Action

```python
@admin.action(description="Delete items", permissions=['delete'])
def delete_items(modeladmin, request, queryset):
    queryset.delete()

class ArticleAdmin(admin.ModelAdmin):
    actions = [delete_items]

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # Custom permission logic
```

## Query Optimization Pattern

```python
@admin.action(description="Process with relations")
def process_with_relations(modeladmin, request, queryset):
    # GOTCHA: Avoid N+1 queries
    queryset = queryset.select_related('category').prefetch_related('tags')
    for obj in queryset:
        obj.category.name  # No extra query
```
