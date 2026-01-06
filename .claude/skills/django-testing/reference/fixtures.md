# Test Data: setUpTestData vs Fixtures

## Quick Comparison

| Feature | setUpTestData() | Fixtures (JSON) |
|---------|----------------|-----------------|
| Speed | Fast | Slow |
| Maintainability | Easy | Hard |
| Type Safety | Yes | No |
| Dynamic Data | Yes | No |
| Best For | Most tests | Rare cases |

**Recommendation:** Use `setUpTestData()` for 99% of tests.

## setUpTestData() (Recommended)

### Basic Usage

```python
from django.test import TestCase
from myapp.models import Article, User

class ArticleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Runs ONCE per test class.
        Use for read-only test data.
        """
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        cls.article = Article.objects.create(
            title='Test Article',
            content='Test content',
            author=cls.user
        )

    def test_article_title(self):
        # cls.article available in all test methods
        self.assertEqual(self.article.title, 'Test Article')

    def test_article_author(self):
        self.assertEqual(self.article.author, self.user)
```

### Performance: setUpTestData vs setUp

```python
# SLOW: setUp() runs before EVERY test
class SlowTests(TestCase):
    def setUp(self):
        # Called 100 times for 100 tests!
        self.user = User.objects.create_user('user')
        self.article = Article.objects.create(title='Test', author=self.user)

    # ... 100 test methods
    # Result: 200 DB writes (2 per test)

# FAST: setUpTestData() runs once
class FastTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Called ONCE for all tests!
        cls.user = User.objects.create_user('user')
        cls.article = Article.objects.create(title='Test', author=cls.user)

    # ... 100 test methods
    # Result: 2 DB writes total (100x faster!)
```

### When to Use setUp() Instead

Use `setUp()` for **mutable** data that changes between tests:

```python
class ArticleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Immutable data - runs once
        cls.user = User.objects.create_user('user')

    def setUp(self):
        # Mutable data - runs per test
        self.client = Client()
        self.temp_file = create_temp_file()

    def tearDown(self):
        # Clean up per-test resources
        self.temp_file.delete()
```

### Bulk Creating Test Data

```python
@classmethod
def setUpTestData(cls):
    cls.user = User.objects.create_user('user')

    # Create many objects efficiently
    cls.articles = Article.objects.bulk_create([
        Article(title=f'Article {i}', author=cls.user)
        for i in range(100)
    ])

    # Store first article for convenience
    cls.article = cls.articles[0]
```

### Important Gotcha

Data in `setUpTestData()` is **shared** across tests:

```python
class ArticleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.article = Article.objects.create(title='Original')

    def test_modify_article(self):
        self.article.title = 'Modified'
        self.article.save()
        self.assertEqual(self.article.title, 'Modified')

    def test_check_article(self):
        # Still "Modified" because same object in memory!
        # Solution: refresh from database
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, 'Original')
```

## Fixtures (JSON Files)

### When to Use Fixtures

Use fixtures only when:
- Loading real production data for demos
- Sharing test data across multiple projects
- Testing data migrations

**For normal tests, prefer setUpTestData().**

### Creating Fixtures

```bash
# Export current data to fixture
python manage.py dumpdata myapp.Article --indent 2 > articles.json
```

### Using Fixtures

```python
from django.test import TestCase

class ArticleTestsWithFixtures(TestCase):
    fixtures = ['users.json', 'articles.json']

    def test_fixture_loaded(self):
        # Data from fixtures is available
        self.assertEqual(Article.objects.count(), 10)
        article = Article.objects.get(pk=1)
        self.assertEqual(article.title, 'Expected Title')
```

### Fixture File Example

```json
[
  {
    "model": "myapp.article",
    "pk": 1,
    "fields": {
      "title": "Test Article",
      "content": "Test content",
      "author": 1,
      "published": true,
      "created": "2024-01-15T12:00:00Z"
    }
  }
]
```

### Problems with Fixtures

1. **Hard to maintain**: JSON editing is error-prone
2. **Slow**: Loaded from files on every test
3. **Brittle**: Breaks when models change
4. **No type safety**: Typos cause runtime errors
5. **Static**: Can't generate dynamic data

```python
# ❌ FIXTURE: Hard to maintain
fixtures = ['users.json', 'articles.json']  # What's in these files?

# ✅ setUpTestData: Clear and maintainable
@classmethod
def setUpTestData(cls):
    cls.user = User.objects.create_user('testuser')
    cls.article = Article.objects.create(
        title='Test Article',
        author=cls.user
    )
```

## Factory Pattern (Advanced)

For complex test data, consider factory_boy:

```python
import factory
from myapp.models import Article, User

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')

class ArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Article

    title = factory.Sequence(lambda n: f'Article {n}')
    author = factory.SubFactory(UserFactory)

# Usage in tests
class ArticleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.articles = ArticleFactory.create_batch(10, author=cls.user)
```

## Summary

**Use setUpTestData() for most tests:**
- Fast (runs once per class)
- Maintainable (Python code)
- Type-safe (IDE support)
- Dynamic (can generate data)

**Use setUp() for:**
- Mutable per-test data
- Client instances
- Temporary files

**Use fixtures rarely:**
- Demo data
- Complex migrations
- Cross-project data

**Use factories for:**
- Complex object creation
- Large test suites
- Realistic test data generation
