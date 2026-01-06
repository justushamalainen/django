# Django Form Widgets Reference

Widgets control how form fields render in HTML. They handle presentation, not validation.

## Common Widgets

### Text Input Widgets

```python
from django import forms

# Single-line text
name = forms.CharField(
    widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your name',
        'maxlength': '100',
    })
)

# Email input (HTML5)
email = forms.EmailField(
    widget=forms.EmailInput(attrs={
        'placeholder': 'user@example.com',
        'autocomplete': 'email',
    })
)

# URL input
website = forms.URLField(
    widget=forms.URLInput(attrs={
        'placeholder': 'https://example.com'
    })
)

# Number input
age = forms.IntegerField(
    widget=forms.NumberInput(attrs={
        'min': '0',
        'max': '150',
        'step': '1',
    })
)

# Password input
password = forms.CharField(
    widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter password',
        'autocomplete': 'current-password',
    })
)

# Hidden input
user_id = forms.IntegerField(widget=forms.HiddenInput())

# Multi-line text
description = forms.CharField(
    widget=forms.Textarea(attrs={
        'rows': 5,
        'cols': 40,
        'placeholder': 'Enter description...',
    })
)
```

### Date/Time Widgets

```python
# HTML5 date picker
birth_date = forms.DateField(
    widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control',
    })
)

# HTML5 time picker
appointment_time = forms.TimeField(
    widget=forms.TimeInput(attrs={
        'type': 'time',
        'class': 'form-control',
    })
)

# HTML5 datetime picker
event_datetime = forms.DateTimeField(
    widget=forms.DateTimeInput(attrs={
        'type': 'datetime-local',
        'class': 'form-control',
    })
)
```

### Choice Widgets

```python
STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('published', 'Published'),
    ('archived', 'Archived'),
]

# Dropdown (select)
status = forms.ChoiceField(
    choices=STATUS_CHOICES,
    widget=forms.Select(attrs={'class': 'form-select'})
)

# Radio buttons
priority = forms.ChoiceField(
    choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
    widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
)

# Single checkbox
agree = forms.BooleanField(
    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
)

# Multiple checkboxes
tags = forms.MultipleChoiceField(
    choices=STATUS_CHOICES,
    widget=forms.CheckboxSelectMultiple,
    required=False
)

# Multi-select dropdown
categories = forms.MultipleChoiceField(
    choices=STATUS_CHOICES,
    widget=forms.SelectMultiple(attrs={
        'class': 'form-select',
        'size': '5',
    })
)
```

### File Upload Widgets

```python
# File upload
document = forms.FileField(
    widget=forms.FileInput(attrs={
        'accept': '.pdf,.doc,.docx',
        'class': 'form-control',
    })
)

# Image upload with clear option (default for FileField)
avatar = forms.ImageField(
    widget=forms.ClearableFileInput(attrs={
        'accept': 'image/*',
        'class': 'form-control',
    })
)
```

## Widget Attributes

### Common HTML Attributes

```python
widget = forms.TextInput(attrs={
    # Styling
    'class': 'form-control',
    'style': 'width: 100%;',

    # HTML5
    'placeholder': 'Enter text...',
    'required': True,
    'readonly': True,
    'disabled': True,
    'autofocus': True,
    'autocomplete': 'name',

    # Constraints
    'maxlength': '100',
    'minlength': '5',
    'pattern': '[A-Za-z]+',
    'min': '0',
    'max': '100',
    'step': '0.01',

    # ARIA (accessibility)
    'aria-label': 'Search',
    'aria-describedby': 'help-text',
    'aria-required': 'true',

    # Custom data attributes
    'data-validate': 'true',
    'data-max-length': '100',
})
```

## Setting Widget Attributes

### Method 1: In Field Definition

```python
class MyForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
```

### Method 2: In __init__

```python
class MyForm(forms.Form):
    name = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter name'
        })
```

### Method 3: ModelForm Meta

```python
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product name'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'description': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-control'
            }),
        }
```

## Common Widget Patterns

### Add Bootstrap Classes to All Fields

```python
class BootstrapForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            widget = field.widget

            if isinstance(widget, (forms.TextInput, forms.EmailInput,
                                   forms.URLInput, forms.NumberInput,
                                   forms.Textarea)):
                widget.attrs['class'] = 'form-control'

            elif isinstance(widget, forms.Select):
                widget.attrs['class'] = 'form-select'

            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = 'form-check-input'
```

### Use Placeholder as Label

```python
class PlaceholderForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if 'placeholder' not in field.widget.attrs:
                field.widget.attrs['placeholder'] = field.label
```

### Make All Fields Read-Only

```python
class ReadOnlyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['readonly'] = True
            # Or disabled for all widget types
            # field.widget.attrs['disabled'] = True
```

### Conditional Widget Selection

```python
class DynamicForm(forms.Form):
    description = forms.CharField()

    def __init__(self, *args, use_textarea=False, **kwargs):
        super().__init__(*args, **kwargs)

        if use_textarea:
            self.fields['description'].widget = forms.Textarea(attrs={'rows': 5})
        else:
            self.fields['description'].widget = forms.TextInput()
```

## Widget Media (CSS/JS)

### Including CSS/JS with Widgets

```python
class CustomWidget(forms.Widget):
    class Media:
        css = {
            'all': ('css/custom-widget.css',)
        }
        js = ('js/custom-widget.js',)
```

### Using Widget Media in Templates

```django
<!DOCTYPE html>
<html>
<head>
    <title>Form</title>
    {{ form.media.css }}
</head>
<body>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Submit</button>
    </form>

    {{ form.media.js }}
</body>
</html>
```

## Widget Best Practices

1. **Use semantic HTML5 input types**: `email`, `url`, `number`, `date` for better mobile UX
2. **Add ARIA attributes**: Improve accessibility for screen readers
3. **Include placeholders**: Guide users on expected input
4. **Use appropriate widgets**: Radio for 2-5 choices, select for many
5. **Set autocomplete attributes**: Help browsers autofill forms
6. **Add CSS classes**: For consistent styling across forms
7. **Test on mobile**: Especially date/time pickers
8. **Keep it simple**: Don't over-customize unless necessary
