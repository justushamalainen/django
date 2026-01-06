# Django Test Classes - Quick Reference

## Class Hierarchy

```
unittest.TestCase
    └── SimpleTestCase (No database)
            ├── TestCase (Database with transactions)
            └── TransactionTestCase (Database without transactions)
                    └── LiveServerTestCase (Live server)
```

## When to Use Each Class

### SimpleTestCase
**Use when:** No database access needed

**Features:**
- ✅ Fastest execution
- ✅ URL routing tests
- ✅ Form validation (without DB)
- ✅ Template rendering
- ✅ Utility functions
- ❌ No database access

**Example:**
```python
from django.test import SimpleTestCase
from django.urls import reverse

class URLTests(SimpleTestCase):
    def test_home_url_resolves(self):
        url = reverse('home')
        self.assertEqual(url, '/')
```

### TestCase (Use This 99% of the Time)
**Use when:** Standard database tests

**Features:**
- ✅ Full database access
- ✅ Fast isolation via transactions
- ✅ `setUpTestData()` for performance
- ✅ Test client included
- ⚠️ Each test wrapped in transaction
- ❌ Cannot test transaction.atomic() behavior

**Example:**
```python
from django.test import TestCase

class ArticleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Run once per class
        cls.article = Article.objects.create(title='Test')

    def test_article_str(self):
        self.assertEqual(str(self.article), 'Test')
```

### TransactionTestCase
**Use when:** Testing transaction behavior (rollback, commit)

**Features:**
- ✅ Test `transaction.atomic()` blocks
- ✅ Test real commits/rollbacks
- ⚠️ Much slower (truncates tables)
- ❌ Cannot use `setUpTestData()`

**Example:**
```python
from django.test import TransactionTestCase
from django.db import transaction

class PaymentTests(TransactionTestCase):
    def test_payment_rollback(self):
        try:
            with transaction.atomic():
                payment = Payment.objects.create(amount=100)
                raise ValueError("Failed")
        except ValueError:
            pass

        # Payment should be rolled back
        self.assertEqual(Payment.objects.count(), 0)
```

### LiveServerTestCase
**Use when:** Integration testing with Selenium

**Features:**
- ✅ Starts live Django server
- ✅ Works with Selenium/Playwright
- ⚠️ Very slow
- ⚠️ Requires browser driver

**Example:**
```python
from django.test import LiveServerTestCase
from selenium import webdriver

class BrowserTests(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def test_login_flow(self):
        self.browser.get(f'{self.live_server_url}/login/')
        # ... test user interactions
```

## Quick Decision Tree

```
Need database?
├─ NO → SimpleTestCase
└─ YES → Testing transaction.atomic()?
    ├─ NO → TestCase (default choice)
    └─ YES → Need browser?
        ├─ NO → TransactionTestCase
        └─ YES → LiveServerTestCase
```

## Performance Comparison

| Class | Speed | Use Case |
|-------|-------|----------|
| SimpleTestCase | ⚡⚡⚡ Fastest | URLs, forms, utilities |
| TestCase | ⚡⚡ Fast | Standard tests (99% of cases) |
| TransactionTestCase | ⚡ Slow | Transaction behavior |
| LiveServerTestCase | 🐌 Slowest | Browser integration |

## Common Mistakes

**❌ Using TransactionTestCase for standard tests:**
```python
class ArticleTests(TransactionTestCase):  # TOO SLOW!
    def test_create(self):
        Article.objects.create(title='Test')
```

**✅ Use TestCase instead:**
```python
class ArticleTests(TestCase):  # FAST!
    def test_create(self):
        Article.objects.create(title='Test')
```

**❌ Using database in SimpleTestCase:**
```python
class MyTests(SimpleTestCase):
    def test_article(self):
        Article.objects.create(title='Test')  # ERROR!
```

**✅ Use TestCase for database:**
```python
class MyTests(TestCase):
    def test_article(self):
        Article.objects.create(title='Test')  # WORKS!
```

## Summary

**Default Choice:** Use `TestCase` for 99% of tests.

**Special Cases:**
- Non-database tests → `SimpleTestCase`
- Transaction testing → `TransactionTestCase`
- Browser testing → `LiveServerTestCase`
