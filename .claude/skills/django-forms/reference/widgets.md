# Django Form Widgets

Widgets control HTML rendering only (not validation).

## Three Ways to Set Widget Attributes

**1. In field definition:**
```python
name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
```

**2. In __init__ (for dynamic attributes):**
```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['name'].widget.attrs.update({'class': 'form-control'})
```

**3. In ModelForm Meta:**
```python
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        }
```

## Common Patterns

**Apply class to all fields:**
```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field in self.fields.values():
        if isinstance(field.widget, (forms.TextInput, forms.Textarea)):
            field.widget.attrs['class'] = 'form-control'
```

**Make all fields read-only:**
```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field in self.fields.values():
        field.widget.attrs['readonly'] = True
```

**Conditional widget:**
```python
def __init__(self, *args, use_textarea=False, **kwargs):
    super().__init__(*args, **kwargs)
    if use_textarea:
        self.fields['description'].widget = forms.Textarea(attrs={'rows': 5})
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
