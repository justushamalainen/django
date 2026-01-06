# Django Field Types Quick Reference

Quick reference for Django model field types and common options.

## Field Types Table

| Field Type | Use Case | Database Type | Key Options |
|-----------|----------|---------------|-------------|
| **CharField** | Short text (names, titles) | VARCHAR(max_length) | max_length (required), choices, unique, db_index |
| **TextField** | Long text (articles, descriptions) | TEXT | blank |
| **SlugField** | URL-friendly strings | VARCHAR(50) | unique, allow_unicode |
| **EmailField** | Email addresses | VARCHAR(254) | unique |
| **URLField** | Web URLs | VARCHAR(200) | max_length |
| **IntegerField** | Whole numbers | INTEGER | default, validators |
| **BigIntegerField** | Very large integers | BIGINT | default |
| **PositiveIntegerField** | Non-negative integers | INTEGER | default |
| **DecimalField** | Precise decimals (money) | DECIMAL | max_digits, decimal_places (required) |
| **FloatField** | Approximate decimals | DOUBLE PRECISION | - |
| **BooleanField** | True/False values | BOOLEAN/TINYINT | default (required) |
| **DateField** | Date only | DATE | auto_now, auto_now_add |
| **DateTimeField** | Date and time | DATETIME/TIMESTAMP | auto_now, auto_now_add |
| **TimeField** | Time only | TIME | - |
| **DurationField** | Time spans | INTERVAL/BIGINT | - |
| **JSONField** | JSON data | JSON/JSONB | default=dict or default=list |
| **UUIDField** | UUID identifiers | UUID/CHAR(32) | default=uuid.uuid4, primary_key |
| **FileField** | File uploads | VARCHAR(100) | upload_to, max_length |
| **ImageField** | Image uploads | VARCHAR(100) | upload_to, height_field, width_field |
| **ForeignKey** | Many-to-one | INTEGER/BIGINT | on_delete (required), related_name |
| **ManyToManyField** | Many-to-many | Junction table | related_name, through, blank |
| **OneToOneField** | One-to-one | INTEGER with UNIQUE | on_delete (required), related_name |

## Common Field Options

### Required vs Optional

```python
# Required field (default)
title = models.CharField(max_length=200)

# Optional with null in database
author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)

# Optional in forms only
description = models.TextField(blank=True)

# Optional in both
notes = models.TextField(null=True, blank=True)
```

**Rules:**
- Text fields: Use `blank=True` only (avoid null=True)
- Non-text fields: Use both `null=True, blank=True`

### Defaults

```python
from django.utils import timezone

# Static default
status = models.CharField(max_length=20, default='draft')

# Callable default (no parentheses!)
created_at = models.DateTimeField(default=timezone.now)

# Mutable defaults (dict, list)
metadata = models.JSONField(default=dict)  # NOT {}
tags = models.JSONField(default=list)      # NOT []
```

### Indexes and Uniqueness

```python
# Single field index
slug = models.SlugField(unique=True, db_index=True)

# Unique constraint in Meta
class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=['author', 'slug'],
            name='unique_author_slug'
        )
    ]

# Compound index
class Meta:
    indexes = [
        models.Index(fields=['status', '-created_at']),
    ]
```

### Choices

```python
class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
```

## Relationship Fields

### ForeignKey (Many-to-One)

```python
class Book(models.Model):
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,      # Delete books when author deleted
        related_name='books'            # Access via author.books.all()
    )

# on_delete options:
# CASCADE - Delete related objects
# PROTECT - Prevent deletion
# SET_NULL - Set to NULL (requires null=True)
# SET_DEFAULT - Set to default (requires default)
# SET() - Set to callable result
# DO_NOTHING - Database integrity error
```

### ManyToManyField

```python
class Article(models.Model):
    tags = models.ManyToManyField(
        'Tag',
        related_name='articles',
        blank=True                      # Allow empty in forms
    )

# Usage:
article.tags.add(tag1, tag2)
article.tags.remove(tag1)
article.tags.set([tag1, tag2])
article.tags.clear()
```

### OneToOneField

```python
class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

# Usage:
user.profile  # Access profile
profile.user  # Access user
```

## Common Patterns

### Timestamps

```python
class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Article(TimestampedModel):
    title = models.CharField(max_length=200)
```

### Money Fields

```python
class Product(models.Model):
    price = models.DecimalField(
        max_digits=10,        # Total digits: 99999999.99
        decimal_places=2      # Cents
    )
```

### Validation

```python
from django.core.validators import MinValueValidator, MaxValueValidator

class Product(models.Model):
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
```

## Performance Tips

1. **Index frequently filtered fields**
   ```python
   status = models.CharField(max_length=20, db_index=True)
   ```

2. **Use appropriate field sizes**
   ```python
   # Bad: Wastes space
   count = models.BigIntegerField()

   # Good: Right size
   count = models.PositiveIntegerField()
   ```

3. **Choose CharField over TextField for short content**
   ```python
   # Good for filtering
   status = models.CharField(max_length=20, db_index=True)

   # Avoid for status fields (harder to index)
   # status = models.TextField()
   ```

4. **Integer vs UUID primary keys**
   - **Integer**: Faster, smaller (4 bytes), sequential
   - **UUID**: Larger (16 bytes), non-guessable, distributed systems
