# Django Form Field Types

## Quick Reference

| Field | Non-obvious Notes |
|-------|-------------------|
| DecimalField | Requires `max_digits`, `decimal_places` |
| BooleanField | If `required=True`, checkbox must be checked |
| ModelChoiceField | Use `queryset=` parameter |
| ModelMultipleChoiceField | Returns queryset, not list |
| ImageField | Requires Pillow library |
| FilePathField | Reads from server filesystem |
| TypedChoiceField | Use `coerce=int` to convert choice values |
| DurationField | Accepts timedelta or string like "1 day, 2:30:00" |

## Key Patterns

**DecimalField for currency:**
```python
price = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0)
```

**HTML5 date picker:**
```python
birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
```

**Radio buttons:**
```python
priority = forms.ChoiceField(
    choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
    widget=forms.RadioSelect
)
```

**Dynamic choices from database:**
```python
category = forms.ModelChoiceField(queryset=Category.objects.all())
```

**Custom validator:**
```python
from django.core.validators import RegexValidator

phone = forms.CharField(
    validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message='Enter a valid phone number')]
)
```

**Validation order:** to_python() → validate() → run_validators() → clean() → clean_<fieldname>()
