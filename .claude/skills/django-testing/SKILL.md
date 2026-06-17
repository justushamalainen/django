# Django Testing Skill

## Quick Start

```python
from django.test import TestCase
from myapp.models import Article

class ArticleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Runs once - fast for read-only data
        cls.article = Article.objects.create(title='Test')

    def test_article_title(self):
        self.assertEqual(self.article.title, 'Test')

    def test_article_detail_view(self):
        response = self.client.get(f'/articles/{self.article.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test')
```

Run tests: `python manage.py test`

## 1. Choose the Right Test Class

### Decision Tree

```
Need database?
├─ NO → SimpleTestCase (URLs, forms, utilities)
└─ YES → Testing transaction.atomic()?
    ├─ NO → TestCase (use this 99% of the time)
    └─ YES → TransactionTestCase
```

### SimpleTestCase - No Database

```python
from django.test import SimpleTestCase
from django.urls import reverse

class URLTests(SimpleTestCase):
    def test_home_url(self):
        url = reverse('home')
        self.assertEqual(url, '/')
```

### TestCase - Standard Tests (Default)

```python
class ArticleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.article = Article.objects.create(title='Test')
```

### TransactionTestCase - Transaction Testing

```python
from django.test import TransactionTestCase
from django.db import transaction

class PaymentTests(TransactionTestCase):
    def test_rollback(self):
        try:
            with transaction.atomic():
                Payment.objects.create(amount=100)
                raise ValueError()
        except ValueError:
            pass
        self.assertEqual(Payment.objects.count(), 0)
```

**See:** [reference/test_classes.md](reference/test_classes.md) for complete guide.

## 2. Client Testing Patterns

### Basic GET Request

```python
def test_article_list_view(self):
    response = self.client.get('/articles/')
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Articles')
    self.assertTemplateUsed(response, 'articles/list.html')
```

### POST Request with Data

```python
def test_create_article(self):
    response = self.client.post('/articles/create/', {
        'title': 'New Article',
        'content': 'Content here'
    })
    self.assertEqual(response.status_code, 302)  # Redirect
    self.assertTrue(Article.objects.filter(title='New Article').exists())
```

### Testing with Authentication

```python
def test_authenticated_access(self):
    user = User.objects.create_user('user', 'user@test.com', 'pass')
    self.client.force_login(user)

    response = self.client.get('/profile/')
    self.assertEqual(response.status_code, 200)
```

### Testing Redirects

```python
def test_login_required_redirects(self):
    response = self.client.get('/profile/')
    self.assertRedirects(response, '/login/?next=/profile/')
```

### Checking Template Context

```python
def test_context_data(self):
    response = self.client.get('/articles/')
    self.assertIn('articles', response.context)
    self.assertEqual(len(response.context['articles']), 10)
```

## 3. Common Assertions

### Response Assertions

```python
# Status codes
self.assertEqual(response.status_code, 200)

# Content
self.assertContains(response, 'Expected text')
self.assertNotContains(response, 'Unexpected text')

# Redirects
self.assertRedirects(response, '/expected/url/')

# Templates
self.assertTemplateUsed(response, 'template.html')
```

### Database Assertions

```python
# Existence
self.assertTrue(Article.objects.filter(title='Test').exists())
self.assertEqual(Article.objects.count(), 5)

# Query optimization
with self.assertNumQueries(1):
    list(Article.objects.all())
```

### Form Assertions

```python
# Form validation
form = ArticleForm(data={'title': ''})
self.assertFalse(form.is_valid())
self.assertIn('title', form.errors)
```

### Email Assertions

```python
from django.core import mail

def test_email_sent(self):
    send_welcome_email('user@example.com')

    self.assertEqual(len(mail.outbox), 1)
    self.assertEqual(mail.outbox[0].to, ['user@example.com'])
```

## 4. Performance with setUpTestData

```python
class ArticleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Runs ONCE per class - 100x faster for read-only data"""
        cls.user = User.objects.create_user('user', 'user@test.com')

        # Bulk create for efficiency
        cls.articles = Article.objects.bulk_create([
            Article(title=f'Article {i}', author=cls.user)
            for i in range(100)
        ])

    def setUp(self):
        """Runs BEFORE EACH test - use for mutable data"""
        self.client = Client()

    def test_article_list(self):
        # cls.articles available here
        response = self.client.get('/articles/')
        self.assertEqual(response.status_code, 200)
```

**See:** [reference/fixtures.md](reference/fixtures.md) for setUpTestData vs fixtures.

## 5. Mocking External Services

```python
from unittest.mock import patch

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

### Mock External API

```python
@patch('myapp.services.requests.get')
def test_weather_api(self, mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {'temp': 72}
    mock_get.return_value = mock_response

    weather = get_weather('NYC')
    self.assertEqual(weather['temp'], 72)
```

### Mock Time

```python
@patch('django.utils.timezone.now')
def test_time_dependent(self, mock_now):
    fixed_time = datetime(2024, 1, 15, tzinfo=timezone.utc)
    mock_now.return_value = fixed_time

    article = Article.objects.create(title='Test')
    self.assertEqual(article.created_at, fixed_time)
```

**See:** [reference/mocking.md](reference/mocking.md) for comprehensive patterns.

## Running Tests

```bash
python manage.py test                                          # All tests
python manage.py test myapp                                    # Specific app
python manage.py test myapp.tests.ArticleTests                 # Specific class
python manage.py test myapp.tests.ArticleTests.test_creation   # Specific test
```

## Reference Files

- [reference/test_classes.md](reference/test_classes.md) - Complete test class guide
- [reference/mocking.md](reference/mocking.md) - Mocking patterns
- [reference/fixtures.md](reference/fixtures.md) - setUpTestData vs fixtures
