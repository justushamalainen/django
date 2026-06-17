# Django Migrations - Safe Patterns

## Safe Schema Changes

### Adding Fields

```python
# Safe: nullable or with default
field=models.CharField(max_length=200, null=True, blank=True)
field=models.CharField(max_length=20, default='draft')
```

### Adding Non-Nullable Fields (Three Steps)

```python
# Step 1: Add as nullable
field=models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)

# Step 2: Data migration
def populate_category(apps, schema_editor):
    Article = apps.get_model('myapp', 'Article')
    Category = apps.get_model('myapp', 'Category')
    default = Category.objects.get_or_create(name='Default')[0]
    Article.objects.filter(category__isnull=True).update(category=default)

operations = [migrations.RunPython(populate_category, migrations.RunPython.noop)]

# Step 3: Make non-nullable
field=models.ForeignKey('Category', on_delete=models.CASCADE)
```

### Removing Fields

```python
# Safe deployment: 1) Remove from code, 2) Deploy, 3) Run migration
migrations.RemoveField(model_name='article', name='old_field')
```

### Renaming Fields

```python
migrations.RenameField(model_name='article', old_name='old', new_name='new')
```

### Adding Indexes

```python
# Standard index
migrations.AddIndex(
    model_name='article',
    index=models.Index(fields=['status', '-created_at'], name='idx_name')
)

# Large tables: use CONCURRENT (PostgreSQL, requires atomic=False)
from django.contrib.postgres.operations import AddIndexConcurrently

class Migration(migrations.Migration):
    atomic = False
    operations = [AddIndexConcurrently(...)]
```

## Data Migrations

```python
# Basic pattern (always use apps.get_model, never import directly)
def forward(apps, schema_editor):
    Article = apps.get_model('myapp', 'Article')
    Article.objects.filter(status__isnull=True).update(status='draft')

def reverse(apps, schema_editor):
    Article = apps.get_model('myapp', 'Article')
    Article.objects.filter(status='draft').update(status=None)

operations = [migrations.RunPython(forward, reverse)]

# Large tables: batch processing
def migrate_batches(apps, schema_editor):
    Model = apps.get_model('myapp', 'Model')
    batch_size = 5000
    queryset = Model.objects.filter(needs_update=True)

    while queryset.exists():
        ids = list(queryset[:batch_size].values_list('id', flat=True))
        Model.objects.filter(id__in=ids).update(field='value')
```

## Merge Conflicts

```bash
python manage.py makemigrations --merge
```

```python
# Merge migration has multiple dependencies
dependencies = [
    ('myapp', '0004_add_status'),
    ('myapp', '0004_add_category'),
]
operations = []  # Empty if no conflicts
```

## Rollback

```bash
python manage.py migrate myapp 0003  # Rollback to specific
python manage.py migrate myapp zero  # Rollback all
```


## Common Pitfalls

```python
# ❌ Never import models directly in data migrations
from myapp.models import Article  # WRONG

# ✓ Always use apps.get_model
Article = apps.get_model('myapp', 'Article')  # CORRECT

# ❌ Changing field type without data migration
# Do: 1) Add new field, 2) Copy data, 3) Remove old

# ❌ CONCURRENT operations need atomic=False
class Migration(migrations.Migration):
    atomic = False  # Required for AddIndexConcurrently
```

## Emergency Commands

```bash
python manage.py migrate --fake myapp 0005  # Mark as applied
python manage.py squashmigrations myapp 0001 0010  # Combine migrations
```
