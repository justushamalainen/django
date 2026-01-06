# Django Form Validation Reference

Clean, practical validation patterns using `clean()` and `clean_<fieldname>()` methods.

## Validation Flow

Django validates forms in this order:

1. **to_python()** - Convert input to Python type
2. **validate()** - Built-in field validation
3. **run_validators()** - Custom validators
4. **clean()** - Field's clean method
5. **clean_<fieldname>()** - Form's field-specific clean method
6. **clean()** - Form's general clean method

## Field-Level Validation: clean_<fieldname>()

Use for validation that concerns a single field.

### Basic Field Validation

```python
from django import forms
from django.core.exceptions import ValidationError

class ProductForm(forms.Form):
    name = forms.CharField(max_length=100)
    price = forms.DecimalField(max_digits=10, decimal_places=2)
    stock = forms.IntegerField()

    def clean_name(self):
        """Validate product name."""
        name = self.cleaned_data.get('name')

        # Strip and validate
        name = name.strip()
        if not name:
            raise ValidationError('Name cannot be empty.')

        # Check for prohibited words
        banned_words = ['spam', 'scam']
        if any(word in name.lower() for word in banned_words):
            raise ValidationError('Name contains prohibited words.')

        return name

    def clean_price(self):
        """Validate price is positive."""
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise ValidationError('Price must be greater than zero.')
        return price

    def clean_stock(self):
        """Validate stock is non-negative."""
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise ValidationError('Stock cannot be negative.')
        return stock
```

### Checking Uniqueness

```python
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_username(self):
        """Check username is unique."""
        username = self.cleaned_data.get('username')

        # Build queryset
        qs = User.objects.filter(username__iexact=username)

        # Exclude current instance when editing
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError('Username already exists.')

        return username
```

### Database Lookups

```python
def clean_email(self):
    """Validate email and check if allowed."""
    email = self.cleaned_data.get('email')

    if email:
        # Check domain whitelist
        allowed_domains = ['company.com', 'partner.org']
        domain = email.split('@')[1]

        if domain not in allowed_domains:
            raise ValidationError(
                f'Email must be from: {", ".join(allowed_domains)}'
            )

        # Check if email is already registered
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email already registered.')

    return email
```

### Data Transformation

```python
def clean_phone(self):
    """Normalize phone number."""
    phone = self.cleaned_data.get('phone')

    if phone:
        # Remove non-numeric characters
        phone = ''.join(filter(str.isdigit, phone))

        # Add country code if missing
        if not phone.startswith('1'):
            phone = '1' + phone

        # Validate length
        if len(phone) != 11:
            raise ValidationError('Enter a valid US phone number.')

    return phone
```

## Form-Level Validation: clean()

Use for validation that involves multiple fields.

### Cross-Field Validation

```python
class EventForm(forms.Form):
    name = forms.CharField(max_length=200)
    start_date = forms.DateField()
    end_date = forms.DateField()
    is_online = forms.BooleanField(required=False)
    venue = forms.CharField(max_length=200, required=False)
    meeting_link = forms.URLField(required=False)

    def clean(self):
        """Validate form data across multiple fields."""
        cleaned_data = super().clean()

        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        is_online = cleaned_data.get('is_online')
        venue = cleaned_data.get('venue')
        meeting_link = cleaned_data.get('meeting_link')

        # Date range validation
        if start_date and end_date:
            if end_date < start_date:
                raise ValidationError('End date must be after start date.')

        # Conditional field requirements
        if is_online:
            if not meeting_link:
                self.add_error('meeting_link', 'Required for online events.')
        else:
            if not venue:
                self.add_error('venue', 'Required for in-person events.')

        return cleaned_data
```

### Using add_error() vs raise ValidationError

```python
def clean(self):
    cleaned_data = super().clean()

    # Option 1: Field-specific error (preferred)
    if some_condition:
        self.add_error('field_name', 'Error message')

    # Option 2: General form error (no specific field)
    if some_other_condition:
        raise ValidationError('General error message')

    # Option 3: Multiple field errors at once
    if multiple_issues:
        raise ValidationError({
            'field1': 'Error for field1',
            'field2': 'Error for field2',
        })

    return cleaned_data
```

## Common Validation Patterns

### Password Confirmation

```python
class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        # Verify old password
        if old_password and not self.user.check_password(old_password):
            self.add_error('old_password', 'Current password is incorrect.')

        # Check new passwords match
        if new_password and confirm_password:
            if new_password != confirm_password:
                self.add_error('confirm_password', 'Passwords do not match.')

        # Ensure new password is different
        if old_password and new_password:
            if old_password == new_password:
                self.add_error('new_password',
                    'New password must be different.')

        return cleaned_data
```

### At Least One Required

```python
class ContactForm(forms.Form):
    email = forms.EmailField(required=False)
    phone = forms.CharField(required=False)
    message = forms.CharField(widget=forms.Textarea)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone')

        if not email and not phone:
            raise ValidationError(
                'Please provide at least one contact method (email or phone).'
            )

        return cleaned_data
```

### Conditional Validation

```python
class ShippingForm(forms.Form):
    shipping_method = forms.ChoiceField(
        choices=[
            ('standard', 'Standard'),
            ('express', 'Express'),
            ('pickup', 'Store Pickup'),
        ]
    )
    address = forms.CharField(required=False)
    city = forms.CharField(required=False)
    zip_code = forms.CharField(required=False)
    store_location = forms.ChoiceField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get('shipping_method')

        if method in ['standard', 'express']:
            # Validate shipping address
            required_fields = ['address', 'city', 'zip_code']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field,
                        f'{field.replace("_", " ").title()} is required for shipping.')

        elif method == 'pickup':
            # Validate store selection
            if not cleaned_data.get('store_location'):
                self.add_error('store_location', 'Please select a store location.')

        return cleaned_data
```

### Range Validation

```python
class DiscountForm(forms.Form):
    discount_type = forms.ChoiceField(
        choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')]
    )
    discount_value = forms.DecimalField(max_digits=10, decimal_places=2)
    min_purchase = forms.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        cleaned_data = super().clean()
        discount_type = cleaned_data.get('discount_type')
        discount_value = cleaned_data.get('discount_value')
        min_purchase = cleaned_data.get('min_purchase')

        if discount_type == 'percentage':
            # Percentage must be 0-100
            if discount_value:
                if discount_value < 0 or discount_value > 100:
                    self.add_error('discount_value',
                        'Percentage must be between 0 and 100.')

        elif discount_type == 'fixed':
            # Fixed discount cannot exceed minimum purchase
            if discount_value and min_purchase:
                if discount_value > min_purchase:
                    self.add_error('discount_value',
                        'Discount cannot exceed minimum purchase amount.')

        return cleaned_data
```

### Age Verification

```python
from datetime import date

class RegistrationForm(forms.Form):
    birth_date = forms.DateField()

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')

        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - (
                (today.month, today.day) < (birth_date.month, birth_date.day)
            )

            if age < 18:
                raise ValidationError('You must be at least 18 years old.')

            if birth_date > today:
                raise ValidationError('Birth date cannot be in the future.')

        return birth_date
```

### File Validation

```python
from django.core.validators import FileExtensionValidator

def validate_file_size(file):
    """Limit file size to 5MB."""
    max_size_mb = 5
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f'File size cannot exceed {max_size_mb}MB.')

class DocumentForm(forms.Form):
    document = forms.FileField(
        validators=[
            validate_file_size,
            FileExtensionValidator(['pdf', 'doc', 'docx'])
        ]
    )

    def clean_document(self):
        """Additional file validation."""
        document = self.cleaned_data.get('document')

        if document:
            # Check file name
            if len(document.name) > 100:
                raise ValidationError('Filename too long (max 100 characters).')

            # Check content type
            valid_types = ['application/pdf',
                          'application/msword',
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document']

            if document.content_type not in valid_types:
                raise ValidationError('Invalid file type.')

        return document
```

## ModelForm Validation

ModelForms have both form and model validation.

```python
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock']

    def clean_name(self):
        """Form-level validation (runs before model validation)."""
        name = self.cleaned_data.get('name')

        # Check for duplicate (excluding current instance)
        qs = Product.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError('A product with this name already exists.')

        return name

    def clean(self):
        """Cross-field validation."""
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        stock = cleaned_data.get('stock')

        # Business logic: expensive items must have limited stock
        if price and stock:
            if price > 10000 and stock > 100:
                raise ValidationError(
                    'High-value items cannot have stock over 100.'
                )

        return cleaned_data
```

## Error Messages

### Custom Error Messages

```python
class RegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        error_messages={
            'required': 'Username is required.',
            'max_length': 'Username cannot exceed 30 characters.',
        }
    )

    age = forms.IntegerField(
        error_messages={
            'required': 'Please enter your age.',
            'invalid': 'Enter a valid number.',
        }
    )
```

### Displaying Errors in Templates

```html
<!-- All form errors -->
{% if form.errors %}
  <div class="alert alert-danger">
    <ul>
      {% for field in form %}
        {% for error in field.errors %}
          <li>{{ field.label }}: {{ error }}</li>
        {% endfor %}
      {% endfor %}
      {% for error in form.non_field_errors %}
        <li>{{ error }}</li>
      {% endfor %}
    </ul>
  </div>
{% endif %}

<!-- Per-field errors -->
<div class="form-group">
  {{ form.username.label_tag }}
  {{ form.username }}
  {% if form.username.errors %}
    <div class="invalid-feedback">
      {{ form.username.errors.0 }}
    </div>
  {% endif %}
</div>

<!-- Non-field errors (from clean() method) -->
{% if form.non_field_errors %}
  <div class="alert alert-danger">
    {{ form.non_field_errors }}
  </div>
{% endif %}
```

## Validation Best Practices

1. **Validate in the right place**:
   - `clean_<fieldname>()` for single field logic
   - `clean()` for cross-field logic
   - Model validators for business rules

2. **Return cleaned data**: Always return from clean methods

3. **Use add_error() for field errors**: Better UX than raising ValidationError

4. **Provide helpful error messages**: Tell users how to fix the issue

5. **Don't duplicate validation**: Use validators for reusable logic

6. **Test edge cases**: Empty values, boundary values, invalid types

7. **Consider performance**: Expensive validation (API calls) should be async or queued

8. **Validate client-side too**: But never trust it—always validate server-side
