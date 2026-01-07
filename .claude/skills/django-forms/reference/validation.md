# Django Form Validation

**Validation order:** to_python() → validate() → run_validators() → field.clean() → clean_<fieldname>() → clean()

## clean_<fieldname>() Patterns

**Checking uniqueness (GOTCHA: exclude current instance):**

```python
def clean_username(self):
    username = self.cleaned_data.get('username')
    qs = User.objects.filter(username__iexact=username)

    # Exclude current instance when editing
    if self.instance.pk:
        qs = qs.exclude(pk=self.instance.pk)

    if qs.exists():
        raise ValidationError('Username already exists.')
    return username
```

## clean() for Cross-Field Validation

```python
def clean(self):
    cleaned_data = super().clean()
    start_date = cleaned_data.get('start_date')
    end_date = cleaned_data.get('end_date')

    # Date range validation
    if start_date and end_date and end_date < start_date:
        raise ValidationError('End date must be after start date.')

    # Conditional requirements
    if cleaned_data.get('is_online'):
        if not cleaned_data.get('meeting_link'):
            self.add_error('meeting_link', 'Required for online events.')
    else:
        if not cleaned_data.get('venue'):
            self.add_error('venue', 'Required for in-person events.')

    return cleaned_data
```

**add_error() vs raise ValidationError:**

```python
# Field-specific error (preferred)
self.add_error('field_name', 'Error message')

# General form error
raise ValidationError('General error message')

# Multiple field errors
raise ValidationError({'field1': 'Error 1', 'field2': 'Error 2'})
```

## Common Patterns

**Password confirmation:**
```python
def clean(self):
    cleaned_data = super().clean()
    new = cleaned_data.get('new_password')
    confirm = cleaned_data.get('confirm_password')

    if new and confirm and new != confirm:
        self.add_error('confirm_password', 'Passwords do not match.')
    return cleaned_data
```

**At least one required:**
```python
def clean(self):
    cleaned_data = super().clean()
    if not cleaned_data.get('email') and not cleaned_data.get('phone'):
        raise ValidationError('Provide at least email or phone.')
    return cleaned_data
```

**File size validation:**

```python
from django.core.validators import FileExtensionValidator

def validate_file_size(file):
    if file.size > 5 * 1024 * 1024:  # 5MB
        raise ValidationError('File size cannot exceed 5MB.')

document = forms.FileField(
    validators=[validate_file_size, FileExtensionValidator(['pdf', 'doc', 'docx'])]
)
```

**Custom error messages:**
```python
username = forms.CharField(
    error_messages={
        'required': 'Username is required.',
        'max_length': 'Username cannot exceed 30 characters.',
    }
)
```
