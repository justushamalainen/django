# Test Data: setUpTestData vs Fixtures

**Recommendation:** Use `setUpTestData()` for 99% of tests. It's faster, more maintainable, and type-safe.

## setUpTestData Pattern

```python
from django.test import TestCase

class ArticleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Runs ONCE per test class - fast for read-only data"""
        cls.user = User.objects.create_user('testuser', 'test@example.com')
        cls.article = Article.objects.create(
            title='Test Article',
            author=cls.user
        )

    def test_article_title(self):
        self.assertEqual(self.article.title, 'Test Article')
```

## Bulk Creating Test Data

```python
@classmethod
def setUpTestData(cls):
    cls.user = User.objects.create_user('user')

    # Create many objects efficiently
    cls.articles = Article.objects.bulk_create([
        Article(title=f'Article {i}', author=cls.user)
        for i in range(100)
    ])
```

## Django Gotcha: Shared State

If you modify objects in `setUpTestData()`, call `refresh_from_db()` to get the original:

```python
@classmethod
def setUpTestData(cls):
    cls.article = Article.objects.create(title='Original')

def test_modify(self):
    self.article.title = 'Modified'
    self.article.save()

def test_check(self):
    self.article.refresh_from_db()  # Get original from DB
    self.assertEqual(self.article.title, 'Original')
```

## Fixtures (Avoid)

Fixtures are JSON files that load test data. Avoid them - they're slow, brittle, and hard to maintain. Use `setUpTestData()` instead.
