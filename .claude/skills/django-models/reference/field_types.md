# Django Field Types Quick Reference

## Field Types

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
# Text fields: Use blank=True only (avoid null=True)
description = models.TextField(blank=True)

# Non-text fields: Use both null=True, blank=True
author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True)
```

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

## ForeignKey on_delete Options

```python
# CASCADE - Delete related objects
# PROTECT - Prevent deletion (raises error)
# SET_NULL - Set to NULL (requires null=True)
# SET_DEFAULT - Set to default (requires default)
# SET() - Set to callable result
# DO_NOTHING - Database integrity error

author = models.ForeignKey(Author, on_delete=models.CASCADE)
```

## Performance Tips

```python
# Use CharField (not TextField) for filterable short content
status = models.CharField(max_length=20, db_index=True)

# Integer vs UUID primary keys:
# - Integer: 4 bytes, faster, sequential
# - UUID: 16 bytes, non-guessable, distributed systems
```
