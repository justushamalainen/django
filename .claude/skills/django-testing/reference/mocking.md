# Mocking Patterns - Quick Reference

## Why Mock?

Mock external dependencies to:
- Make tests fast (no real API calls)
- Make tests reliable (no network failures)
- Test error conditions
- Avoid costs

## Basic Patterns

### 1. Mock Functions with @patch

```python
from unittest.mock import patch
from django.test import TestCase

@patch('myapp.services.send_email')
def test_notification(self, mock_send_email):
    mock_send_email.return_value = True

    notify_user('user@example.com', 'Hello')

    mock_send_email.assert_called_once_with(
        to='user@example.com',
        subject='Notification',
        body='Hello'
    )
```

**Important:** Patch where the object is USED, not where it's defined.

```python
# myapp/services.py
from external_lib import send_sms

def notify_by_sms(phone, message):
    return send_sms(phone, message)

# tests.py - CORRECT
@patch('myapp.services.send_sms')  # Patch where it's imported
def test_sms(self, mock_sms):
    notify_by_sms('+1234567890', 'Test')

# tests.py - WRONG
@patch('external_lib.send_sms')  # Won't work!
def test_sms(self, mock_sms):
    notify_by_sms('+1234567890', 'Test')
```

### 2. Mock Multiple Functions

```python
@patch('myapp.services.send_email')
@patch('myapp.services.send_sms')
def test_multi_channel(self, mock_sms, mock_email):
    # Note: parameters in REVERSE order!
    mock_email.return_value = True
    mock_sms.return_value = True

    notify_user_all_channels('user@example.com', '+1234567890')

    mock_email.assert_called_once()
    mock_sms.assert_called_once()
```

### 3. Context Manager Mocking

```python
def test_temporary_mock(self):
    with patch('myapp.services.external_api') as mock_api:
        mock_api.return_value = {'status': 'ok'}
        result = my_function()
        self.assertEqual(result, 'ok')
    # Mock only active within the 'with' block
```

## Common Mocking Scenarios

### Mock External APIs

```python
@patch('myapp.services.requests.get')
def test_weather_api(self, mock_get):
    # Configure mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'temperature': 72,
        'conditions': 'sunny'
    }
    mock_get.return_value = mock_response

    weather = get_weather('New York')

    mock_get.assert_called_once()
    self.assertEqual(weather['temperature'], 72)
```

### Mock Payment APIs (Stripe)

```python
@patch('myapp.services.stripe.Charge.create')
def test_payment(self, mock_charge_create):
    # Configure mock
    mock_charge = Mock()
    mock_charge.id = 'ch_123456'
    mock_charge.status = 'succeeded'
    mock_charge_create.return_value = mock_charge

    result = process_payment(order, token='tok_test')

    mock_charge_create.assert_called_once_with(
        amount=5000,
        currency='usd',
        source='tok_test'
    )
    self.assertTrue(result.success)
```

### Mock Django Email

```python
from django.core import mail

class EmailTests(TestCase):
    def test_welcome_email(self):
        # No mocking needed - Django captures emails
        send_welcome_email('user@example.com')

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ['user@example.com'])
        self.assertEqual(email.subject, 'Welcome!')
```

### Mock Time/Dates

```python
from unittest.mock import patch
from django.utils import timezone
from datetime import datetime

@patch('django.utils.timezone.now')
def test_time_dependent(self, mock_now):
    fixed_time = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
    mock_now.return_value = fixed_time

    article = Article.objects.create(title='Test')
    self.assertEqual(article.created_at, fixed_time)
```

**Or use freezegun:**

```python
from freezegun import freeze_time

@freeze_time("2024-01-15 12:00:00")
def test_with_frozen_time(self):
    article = Article.objects.create(title='Test')
    # Time is frozen at 2024-01-15 12:00:00
```

### Mock File Uploads

```python
from django.core.files.uploadedfile import SimpleUploadedFile

def test_image_upload(self):
    image = SimpleUploadedFile(
        name='test.jpg',
        content=b'fake image content',
        content_type='image/jpeg'
    )

    article = Article.objects.create(title='Test', image=image)
    self.assertTrue(article.image)

    # Clean up
    article.image.delete()
```

### Mock Celery Tasks

```python
@patch('myapp.tasks.send_notification.delay')
def test_async_task(self, mock_task):
    article = Article.objects.create(title='Test')
    notify_subscribers(article)

    # Verify task was queued
    mock_task.assert_called_once_with(article.id)
```

## Advanced Patterns

### Side Effects (Multiple Returns)

```python
@patch('myapp.services.external_api')
def test_polling(self, mock_api):
    # Return different values on each call
    mock_api.side_effect = [
        {'status': 'pending'},
        {'status': 'processing'},
        {'status': 'complete'}
    ]

    status = poll_until_complete()
    self.assertEqual(status, 'complete')
    self.assertEqual(mock_api.call_count, 3)
```

### Side Effects (Exceptions)

```python
@patch('myapp.services.risky_operation')
def test_exception_handling(self, mock_operation):
    mock_operation.side_effect = ValueError('Invalid input')

    with self.assertRaises(ValueError):
        perform_operation()
```

### Mock Class Instances

```python
@patch('myapp.services.APIClient')
def test_api_client(self, MockAPIClient):
    # Configure mock instance
    mock_instance = MockAPIClient.return_value
    mock_instance.get_data.return_value = {'status': 'ok'}

    service = MyService()
    result = service.fetch_data()

    mock_instance.get_data.assert_called_once()
    self.assertEqual(result['status'], 'ok')
```

## Best Practices

### 1. Patch at the Right Level

```python
# ❌ BAD: Too broad
@patch('requests.get')  # Affects EVERYTHING
def test_my_function(self, mock_get):
    pass

# ✅ GOOD: Specific
@patch('myapp.services.requests.get')  # Only this module
def test_my_function(self, mock_get):
    pass
```

### 2. Don't Mock Django ORM

```python
# ❌ BAD: Mocking Django (tests nothing)
@patch('Article.objects.create')
def test_article(self, mock_create):
    pass

# ✅ GOOD: Test real database
def test_article(self):
    article = Article.objects.create(title='Test')
    self.assertEqual(article.title, 'Test')
```

### 3. Use Specific Assertions

```python
@patch('myapp.services.send_email')
def test_notification(self, mock_send):
    notify_user('user@example.com')

    # ❌ BAD: Vague
    mock_send.assert_called()

    # ✅ GOOD: Specific
    mock_send.assert_called_once_with(
        to='user@example.com',
        subject='Notification'
    )
```

### 4. Don't Over-Mock

```python
# ❌ BAD: Too much mocking (tests nothing real)
@patch('myapp.services.function_a')
@patch('myapp.services.function_b')
@patch('myapp.services.function_c')
def test_workflow(self, mock_c, mock_b, mock_a):
    pass

# ✅ GOOD: Only mock external dependencies
@patch('myapp.services.external_api_call')
def test_workflow(self, mock_api):
    # Rest runs normally
    pass
```

## Common Pitfalls

### Wrong Patch Target

```python
# module.py
from datetime import datetime

def get_timestamp():
    return datetime.now()

# ❌ WRONG
@patch('datetime.datetime.now')  # Won't work!
def test_timestamp(self, mock_now):
    pass

# ✅ CORRECT
@patch('module.datetime.now')  # Patch where imported
def test_timestamp(self, mock_now):
    pass
```

### Forgetting return_value

```python
@patch('myapp.services.get_data')
def test_processing(self, mock_get_data):
    # ❌ WRONG: Returns Mock object by default
    result = process_data()  # result is a Mock!

    # ✅ CORRECT: Set return value
    mock_get_data.return_value = {'key': 'value'}
    result = process_data()  # Now result is the dict
```

## Summary

**Key Points:**
- Mock external dependencies (APIs, emails, files)
- Patch where objects are USED, not defined
- Use `mock.return_value` for return values
- Use `mock.side_effect` for multiple returns or exceptions
- Use `assert_called_once_with()` to verify calls
- Don't mock Django's ORM or internals
- Don't over-mock - test real code when possible

**Most Common Patterns:**
- `@patch('module.function')` - Mock functions
- `mock.return_value = X` - Set return value
- `mock.side_effect = [X, Y, Z]` - Multiple returns
- `mock.assert_called_once_with(args)` - Verify exact call
- `@freeze_time()` - Mock time (requires freezegun)
