# Django Forms Skill

**Use for:** ModelForms, validation logic, file uploads, formsets.

**ModelForm vs Form:** Use ModelForm when saving to database, Form otherwise.

## Validation

**clean_<fieldname>() - GOTCHA: exclude instance.pk when checking uniqueness:**
```python
def clean_name(self):
    name = self.cleaned_data.get('name')
    qs = Product.objects.filter(name__iexact=name)
    if self.instance.pk:  # Exclude current instance when editing
        qs = qs.exclude(pk=self.instance.pk)
    if qs.exists():
        raise forms.ValidationError('Already exists.')
    return name
```

**clean() for cross-field validation:**
```python
def clean(self):
    cleaned_data = super().clean()
    if cleaned_data.get('end_date') < cleaned_data.get('start_date'):
        raise forms.ValidationError('End date must be after start date.')
    # Use self.add_error('field_name', 'message') to attach error to specific field
    return cleaned_data
```

## Widgets

**Set in ModelForm.Meta:**
```python
class Meta:
    widgets = {
        'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
    }
```

**Apply to all fields in __init__:**
```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field in self.fields.values():
        field.widget.attrs['class'] = 'form-control'
```

## Formsets

```python
from django.forms import inlineformset_factory

OrderItemFormSet = inlineformset_factory(
    Order, OrderItem, fields=['product', 'quantity'],
    extra=3, can_delete=True, min_num=1
)

formset = OrderItemFormSet(request.POST, instance=order)
```

**GOTCHA: {{ formset.management_form }} required in template**

## File Uploads

**GOTCHA: Need request.FILES in view and enctype in template:**
```python
form = ProfileForm(request.POST, request.FILES, instance=obj)
```
```html
<form method="post" enctype="multipart/form-data">
```

## Patterns

**commit=False to add data:**
```python
obj = form.save(commit=False)
obj.created_by = request.user
obj.save()
```

**Dynamic choices in __init__:**
```python
self.fields['category'].choices = [(c.id, c.name) for c in Category.objects.all()]
```

## Key Gotchas

- Always include {% csrf_token %} in POST forms
- Always return cleaned_data from clean methods
- Exclude instance.pk when checking uniqueness in clean_<fieldname>()
- File uploads need request.FILES and enctype="multipart/form-data"
- Formsets need {{ formset.management_form }}
