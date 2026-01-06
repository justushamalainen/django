# Django Form Field Types Reference

Quick reference for all Django form field types.

## Field Type Table

| Field Type | Widget | HTML Type | Common Use | Validation |
|------------|---------|-----------|------------|------------|
| CharField | TextInput | text | Short text | max_length, min_length |
| EmailField | EmailInput | email | Email addresses | Valid email format |
| URLField | URLInput | url | URLs | Valid URL with scheme |
| SlugField | TextInput | text | URL slugs | Letters, numbers, -, _ only |
| IntegerField | NumberInput | number | Integers | min_value, max_value |
| FloatField | NumberInput | number | Decimals | min_value, max_value |
| DecimalField | NumberInput | number | Money, precise decimals | max_digits, decimal_places |
| BooleanField | CheckboxInput | checkbox | Yes/No | Must be checked if required |
| DateField | DateInput | text/date | Dates | Valid date format |
| TimeField | TimeInput | text/time | Times | Valid time format |
| DateTimeField | DateTimeInput | text/datetime-local | Date + time | Valid datetime format |
| DurationField | TextInput | text | Time durations | Timedelta format |
| ChoiceField | Select | select | Single selection | Value in choices |
| MultipleChoiceField | SelectMultiple | select multiple | Multiple selections | Values in choices |
| TypedChoiceField | Select | select | Typed single selection | Coerced type |
| ModelChoiceField | Select | select | Select from queryset | Valid model instance |
| ModelMultipleChoiceField | SelectMultiple | select multiple | Multiple from queryset | Valid model instances |
| FileField | ClearableFileInput | file | File uploads | File validators |
| ImageField | ClearableFileInput | file | Image uploads | Valid image + Pillow |
| FilePathField | Select | select | Server file selection | Valid file path |
| JSONField | Textarea | textarea | JSON data | Valid JSON |
| UUIDField | TextInput | text | UUIDs | Valid UUID format |
| GenericIPAddressField | TextInput | text | IP addresses | Valid IPv4/IPv6 |

## Common Field Parameters

```python
field = forms.CharField(
    required=True,              # Field must have a value
    label='Field Label',        # Display label
    initial='default',          # Default value
    help_text='Help message',   # Help text below field
    widget=forms.TextInput(),   # Custom widget
    validators=[],              # List of validators
    error_messages={},          # Custom error messages
    disabled=False,             # Disable input
    localize=False,            # Use localized formatting
)
```

## Text Fields

```python
# Short text
name = forms.CharField(max_length=100)

# Long text
description = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}))

# Email with validation
email = forms.EmailField()

# URL with validation
website = forms.URLField(required=False)

# Slug for URLs
slug = forms.SlugField(max_length=50)
```

## Numeric Fields

```python
# Integer
age = forms.IntegerField(min_value=0, max_value=150)

# Decimal (for currency)
price = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0)

# Float
rating = forms.FloatField(min_value=0.0, max_value=5.0)
```

## Date/Time Fields

```python
# Date with HTML5 picker
birth_date = forms.DateField(
    widget=forms.DateInput(attrs={'type': 'date'})
)

# Time
appointment_time = forms.TimeField(
    widget=forms.TimeInput(attrs={'type': 'time'})
)

# DateTime
event_start = forms.DateTimeField(
    widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
)
```

## Choice Fields

```python
STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('published', 'Published'),
    ('archived', 'Archived'),
]

# Dropdown
status = forms.ChoiceField(choices=STATUS_CHOICES)

# Radio buttons
priority = forms.ChoiceField(
    choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
    widget=forms.RadioSelect
)

# Multiple checkboxes
tags = forms.MultipleChoiceField(
    choices=STATUS_CHOICES,
    widget=forms.CheckboxSelectMultiple,
    required=False
)

# From database
from .models import Category
category = forms.ModelChoiceField(queryset=Category.objects.all())
```

## File Fields

```python
from django.core.validators import FileExtensionValidator

# Generic file upload
document = forms.FileField(
    validators=[FileExtensionValidator(['pdf', 'doc', 'docx'])]
)

# Image upload (requires Pillow)
avatar = forms.ImageField(
    required=False,
    validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])]
)
```

## Custom Validation

```python
from django.core.validators import RegexValidator

phone = forms.CharField(
    validators=[
        RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message='Enter a valid phone number'
        )
    ]
)
```

## Field Validation Order

1. **to_python()** - Convert to Python type
2. **validate()** - Built-in validation
3. **run_validators()** - Custom validators
4. **clean()** - Field clean method
5. **clean_<fieldname>()** - Form field clean method
