# Django Forms Skill

## Overview

This skill helps you create and validate Django forms. Forms handle user input, validation, data cleaning, and HTML rendering.

**Use this skill for:** Creating forms for data entry, building ModelForms, validation logic, file uploads, and formsets.

## Quick Start

```python
# forms.py
from django import forms
from .models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'published']
        widgets = {'content': forms.Textarea(attrs={'rows': 5})}

# views.py
def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('article_list')
    else:
        form = ArticleForm()
    return render(request, 'article_form.html', {'form': form})

# template
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Save</button>
</form>
```

## Form vs ModelForm

**Use ModelForm:** When saving to database, want automatic field generation, CRUD operations.

**Use Form:** When not saving to database (search, login, contact), fields not in any model, API validation, multi-step wizards.

```python
# ModelForm - database operations
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description']

# Form - non-database operations
class SearchForm(forms.Form):
    query = forms.CharField(max_length=100)
    category = forms.ChoiceField(choices=CATEGORIES)
```

## Validation Patterns

### Single Field: clean_<fieldname>()

```python
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price']

    def clean_name(self):
        name = self.cleaned_data.get('name')

        # Check uniqueness (excluding current instance)
        qs = Product.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError('Product name already exists.')

        return name

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price < 0:
            raise forms.ValidationError('Price cannot be negative.')
        return price
```

### Cross-Field: clean()

```python
class EventForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()
    is_online = forms.BooleanField(required=False)
    venue = forms.CharField(required=False)
    meeting_link = forms.URLField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Date range validation
        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError('End date must be after start date.')

        # Conditional requirements
        if cleaned_data.get('is_online'):
            if not cleaned_data.get('meeting_link'):
                self.add_error('meeting_link', 'Required for online events.')
        else:
            if not cleaned_data.get('venue'):
                self.add_error('venue', 'Required for in-person events.')

        return cleaned_data
```

## Widget Customization

### Add CSS Classes

```python
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
```

### Apply to All Fields

```python
class BootstrapForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.Textarea,
                                        forms.EmailInput, forms.NumberInput)):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
```

### HTML5 Input Types

```python
class ContactForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'type': 'email'}))
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    age = forms.IntegerField(widget=forms.NumberInput(attrs={'min': '0', 'max': '150'}))
```

## Formsets

Handle multiple forms on one page:

```python
from django.forms import inlineformset_factory
from .models import Order, OrderItem

OrderItemFormSet = inlineformset_factory(
    Order, OrderItem,
    fields=['product', 'quantity', 'price'],
    extra=3, can_delete=True, min_num=1, validate_min=True
)

def order_update(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        formset = OrderItemFormSet(request.POST, instance=order)
        if formset.is_valid():
            formset.save()
            return redirect('order_detail', pk=order.pk)
    else:
        formset = OrderItemFormSet(instance=order)

    return render(request, 'order_form.html', {'formset': formset})
```

**Template:**
```html
<form method="post">
  {% csrf_token %}
  {{ formset.management_form }}  <!-- Required! -->
  {% for form in formset %}
    {{ form.as_p }}
  {% endfor %}
  <button type="submit">Save</button>
</form>
```

## File Upload

```python
from django.core.validators import FileExtensionValidator

def validate_file_size(file):
    if file.size > 5 * 1024 * 1024:  # 5MB
        raise forms.ValidationError('File size cannot exceed 5MB.')

class ProfileForm(forms.ModelForm):
    avatar = forms.ImageField(
        required=False,
        validators=[validate_file_size, FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])]
    )
    class Meta:
        model = Profile
        fields = ['avatar', 'bio']
```

**View:**
```python
def profile_update(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'profile_form.html', {'form': form})
```

**Template:**
```html
<form method="post" enctype="multipart/form-data">  <!-- Required! -->
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Update</button>
</form>
```

## Common Patterns

### Save with commit=False

```python
if form.is_valid():
    product = form.save(commit=False)
    product.created_by = request.user
    product.save()
```

### Dynamic Choices

```python
class ProductForm(forms.Form):
    category = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].choices = [(c.id, c.name) for c in Category.objects.all()]
```

## Reference Files

- **Field Types:** `/home/user/django/.claude/skills/django-forms/reference/field_types.md`
- **Validation:** `/home/user/django/.claude/skills/django-forms/reference/validation.md`
- **Widgets:** `/home/user/django/.claude/skills/django-forms/reference/widgets.md`

## Best Practices

1. Always validate server-side (never trust client-side only)
2. Use ModelForm when saving to database
3. Use commit=False when adding extra data before save
4. Always include {% csrf_token %} in POST forms
5. Use clean_<fieldname>() for single field validation
6. Use clean() for cross-field validation
7. Always return cleaned_data from clean methods
8. Provide helpful, actionable error messages
