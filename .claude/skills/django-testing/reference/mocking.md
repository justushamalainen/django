# Mocking Patterns - Quick Reference

## Basic Pattern

```python
from unittest.mock import patch

@patch('myapp.services.send_email')  # Patch where it's USED, not defined
def test_notification(self, mock_send_email):
    mock_send_email.return_value = True

    notify_user('user@example.com', 'Hello')

    mock_send_email.assert_called_once_with(
        to='user@example.com',
        subject='Notification',
        body='Hello'
    )
```

## Django-Specific Patterns

### Django Email (No Mocking Needed)

```python
from django.core import mail

def test_welcome_email(self):
    send_welcome_email('user@example.com')

    self.assertEqual(len(mail.outbox), 1)
    self.assertEqual(mail.outbox[0].to, ['user@example.com'])
```

### Mock Time

```python
@patch('django.utils.timezone.now')
def test_time_dependent(self, mock_now):
    fixed_time = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
    mock_now.return_value = fixed_time

    article = Article.objects.create(title='Test')
    self.assertEqual(article.created_at, fixed_time)
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
    article.image.delete()  # Clean up
```

### Mock Celery Tasks

```python
@patch('myapp.tasks.send_notification.delay')
def test_async_task(self, mock_task):
    article = Article.objects.create(title='Test')
    notify_subscribers(article)

    mock_task.assert_called_once_with(article.id)
```

## Common Patterns

### Side Effects (Multiple Returns)

```python
@patch('myapp.services.external_api')
def test_polling(self, mock_api):
    mock_api.side_effect = [
        {'status': 'pending'},
        {'status': 'processing'},
        {'status': 'complete'}
    ]

    status = poll_until_complete()
    self.assertEqual(status, 'complete')
```

### Mock External API

```python
@patch('myapp.services.requests.get')
def test_api(self, mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {'temp': 72}
    mock_get.return_value = mock_response

    result = get_weather('NYC')
    self.assertEqual(result['temp'], 72)
```
