# Django Models & ORM Skill

## Quick Model Definition

### Basic Model

```python
from django.db import models

class Article(models.Model):
    # Text fields
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()

    # Choices
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return self.title
```

### Relationships

```python
class Author(models.Model):
    name = models.CharField(max_length=100)

class Category(models.Model):
    name = models.CharField(max_length=50)

class Article(models.Model):
    title = models.CharField(max_length=200)

    # ForeignKey (Many-to-One)
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,      # Delete articles when author deleted
        related_name='articles'        # Access: author.articles.all()
    )

    # ManyToMany
    tags = models.ManyToManyField(
        'Tag',
        related_name='articles',
        blank=True
    )

# OneToOne (for profile/settings)
class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(blank=True)
```

## N+1 Query Detection

```python
# BAD: N+1 queries
articles = Article.objects.all()  # 1 query
for article in articles:
    print(article.author.name)    # N queries!

# GOOD: select_related for ForeignKey/OneToOne (SQL JOIN)
articles = Article.objects.select_related('author')

# GOOD: prefetch_related for ManyToMany/reverse FK (separate queries)
articles = Article.objects.prefetch_related('tags')

# Combine both
articles = Article.objects.select_related('author').prefetch_related('tags')
```

## Common Query Patterns

### Filtering and Lookups

```python
# Basic filtering
Article.objects.filter(status='published')
Article.objects.filter(views__gte=100)
Article.objects.filter(title__icontains='django')

# Complex queries with Q objects
from django.db.models import Q

Article.objects.filter(
    Q(status='published') | Q(featured=True)
)

# Exclude
Article.objects.exclude(status='draft')
```

### Counting and Aggregation

```python
from django.db.models import Count, Avg, Sum

# Count related objects
authors = Author.objects.annotate(
    article_count=Count('articles')
).filter(article_count__gte=5)

# Aggregation
Article.objects.aggregate(
    total=Count('id'),
    avg_views=Avg('views')
)
```

### Atomic Updates

```python
from django.db.models import F

# Atomic increment (no race conditions)
Article.objects.filter(pk=1).update(views=F('views') + 1)

# Compare fields
Article.objects.filter(views__gt=F('likes'))
```

### Bulk Operations

```python
# Bulk create
Article.objects.bulk_create([
    Article(title='Article 1'),
    Article(title='Article 2'),
], batch_size=1000)

# Bulk update (efficient)
Article.objects.filter(status='draft').update(status='published')
```

## Safe Migration Pattern for Non-Nullable Fields

```python
# When table has existing data, use 3 steps:

# Step 1: Add as nullable
status = models.CharField(max_length=20, null=True)

# Step 2: Data migration to populate values
def populate_status(apps, schema_editor):
    Article = apps.get_model('myapp', 'Article')
    Article.objects.filter(status__isnull=True).update(status='draft')

# Step 3: Make non-nullable
status = models.CharField(max_length=20, default='draft')
```

See [migration_ops.md](reference/migration_ops.md) for migration patterns.

## Anti-Patterns to Avoid

### 1. N+1 Queries in Loops
```python
# BAD
for article in Article.objects.all():
    print(article.author.name)  # Extra query per article

# GOOD
for article in Article.objects.select_related('author'):
    print(article.author.name)  # No extra queries
```

### 2. Using .count() When You Need .exists()
```python
# BAD
if Article.objects.filter(status='published').count() > 0:

# GOOD
if Article.objects.filter(status='published').exists():
```

### 3. Not Using Atomic Updates
```python
# BAD: Race condition
article.views = article.views + 1
article.save()

# GOOD: Atomic
Article.objects.filter(pk=article.pk).update(views=F('views') + 1)
```

