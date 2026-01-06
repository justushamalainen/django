# Django Models & ORM Skill

Essential Django ORM patterns for everyday development.

## When to Use This Skill

**Use this skill for:**
- Creating or modifying model schemas
- Optimizing database queries (N+1 problems)
- Working with relationships (ForeignKey, ManyToMany, OneToOne)
- Writing efficient QuerySets
- Handling migrations safely

**Use other skills for:**
- Views and business logic (django-views)
- Admin customization (django-admin)
- Forms (django-forms)

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

**The Problem:** Loading related objects in a loop causes extra queries.

```python
# BAD: N+1 queries
articles = Article.objects.all()  # 1 query
for article in articles:
    print(article.author.name)    # N queries!
```

**The Solutions:**

```python
# GOOD: Use select_related for ForeignKey/OneToOne
articles = Article.objects.select_related('author')
for article in articles:
    print(article.author.name)    # No extra queries

# GOOD: Use prefetch_related for ManyToMany/reverse FK
articles = Article.objects.prefetch_related('tags')
for article in articles:
    print([t.name for t in article.tags.all()])  # No extra queries

# Combine both
articles = Article.objects.select_related('author').prefetch_related('tags')
```

**When to use each:**
- `select_related()`: ForeignKey, OneToOneField (uses SQL JOIN)
- `prefetch_related()`: ManyToManyField, reverse ForeignKey (separate queries)

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

## Migration Basics

### Common Workflow: Add Field to Model

```python
# 1. Add field to model
class Article(models.Model):
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, default='draft')  # New field

# 2. Generate migration
# $ python manage.py makemigrations

# 3. Review and apply
# $ python manage.py migrate
```

### Adding Non-Nullable Field (Safe Pattern)

```python
# If table has existing data, use 3 steps:

# Step 1: Add as nullable
status = models.CharField(max_length=20, null=True)

# Step 2: Create data migration to populate values
def populate_status(apps, schema_editor):
    Article = apps.get_model('myapp', 'Article')
    Article.objects.filter(status__isnull=True).update(status='draft')

# Step 3: Make non-nullable
status = models.CharField(max_length=20, default='draft')
```

### Migration Commands

```bash
# Create migration
python manage.py makemigrations myapp

# Apply migrations
python manage.py migrate

# Check status
python manage.py showmigrations

# Rollback to specific migration
python manage.py migrate myapp 0003

# Merge conflicts
python manage.py makemigrations --merge
```

## Field Types Quick Reference

| Field | Use For | Example |
|-------|---------|---------|
| CharField | Short text | `models.CharField(max_length=200)` |
| TextField | Long text | `models.TextField()` |
| IntegerField | Numbers | `models.IntegerField(default=0)` |
| BooleanField | True/False | `models.BooleanField(default=False)` |
| DateTimeField | Timestamps | `models.DateTimeField(auto_now_add=True)` |
| DecimalField | Money | `models.DecimalField(max_digits=10, decimal_places=2)` |
| ForeignKey | Many-to-one | `models.ForeignKey(Author, on_delete=models.CASCADE)` |
| ManyToManyField | Many-to-many | `models.ManyToManyField('Tag', blank=True)` |

See [field_types.md](reference/field_types.md) for complete reference.

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

## Reference Files

- [field_types.md](reference/field_types.md) - All field types and options
- [query_patterns.md](reference/query_patterns.md) - The 5 essential query optimization patterns
- [migration_ops.md](reference/migration_ops.md) - Safe migration patterns for production
