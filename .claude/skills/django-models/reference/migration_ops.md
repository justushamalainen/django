# Django Migrations - Safe Patterns

Practical guide to safe Django migrations for production environments.

## Migration Basics

### Creating and Applying

```bash
# Create migration
python manage.py makemigrations myapp

# Apply migrations
python manage.py migrate

# Show status
python manage.py showmigrations

# Show SQL (review before applying)
python manage.py sqlmigrate myapp 0001

# Check for issues
python manage.py makemigrations --check
```

## Safe Schema Changes

### Adding Fields (Safe)

```python
# Nullable field - Safe, no default needed
migrations.AddField(
    model_name='article',
    name='subtitle',
    field=models.CharField(max_length=200, null=True, blank=True),
)

# Field with default - Safe
migrations.AddField(
    model_name='article',
    name='status',
    field=models.CharField(max_length=20, default='draft'),
)
```

### Adding Non-Nullable Fields (Two-Step)

When adding a non-nullable field to a table with existing data:

```python
# Step 1: Add as nullable
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name='article',
            name='category',
            field=models.ForeignKey(
                'Category',
                on_delete=models.SET_NULL,
                null=True
            ),
        ),
    ]

# Step 2: Populate data (separate migration)
def populate_category(apps, schema_editor):
    Article = apps.get_model('myapp', 'Article')
    Category = apps.get_model('myapp', 'Category')

    default_category = Category.objects.get_or_create(
        name='Uncategorized',
        defaults={'slug': 'uncategorized'}
    )[0]

    Article.objects.filter(category__isnull=True).update(category=default_category)

class Migration(migrations.Migration):
    dependencies = [('myapp', '0002_add_category_field')]

    operations = [
        migrations.RunPython(populate_category, migrations.RunPython.noop),
    ]

# Step 3: Make non-nullable (if needed)
class Migration(migrations.Migration):
    operations = [
        migrations.AlterField(
            model_name='article',
            name='category',
            field=models.ForeignKey('Category', on_delete=models.CASCADE),
        ),
    ]
```

### Removing Fields (Safe)

```python
# Simple removal
migrations.RemoveField(
    model_name='article',
    name='old_field',
)

# Safe deployment process:
# 1. Remove field usage from code
# 2. Deploy code (field still in database)
# 3. Create and deploy migration
```

### Renaming Fields (Safe)

```python
# Django handles the database rename automatically
migrations.RenameField(
    model_name='article',
    old_name='publish_date',
    new_name='published_at',
)
```

### Adding Indexes (Safe)

```python
# Add index
migrations.AddIndex(
    model_name='article',
    index=models.Index(
        fields=['status', '-created_at'],
        name='status_created_idx'
    ),
)

# For large tables, use CONCURRENT (PostgreSQL only)
from django.contrib.postgres.operations import AddIndexConcurrently

class Migration(migrations.Migration):
    atomic = False  # Required for CONCURRENT

    operations = [
        AddIndexConcurrently(
            model_name='article',
            index=models.Index(fields=['status'], name='status_idx'),
        ),
    ]
```

## Data Migrations

### Basic Pattern

```python
def forward_migration(apps, schema_editor):
    """Migrate data forward"""
    Article = apps.get_model('myapp', 'Article')

    # Update data
    Article.objects.filter(status__isnull=True).update(status='draft')

def reverse_migration(apps, schema_editor):
    """Reverse the migration"""
    Article = apps.get_model('myapp', 'Article')

    # Revert data
    Article.objects.filter(status='draft').update(status=None)

class Migration(migrations.Migration):
    dependencies = [('myapp', '0001_initial')]

    operations = [
        migrations.RunPython(forward_migration, reverse_migration),
    ]
```

### Batch Processing for Large Tables

```python
def migrate_large_table(apps, schema_editor):
    """Process large table in batches"""
    Article = apps.get_model('myapp', 'Article')

    batch_size = 5000
    articles = Article.objects.filter(status__isnull=True)
    total = articles.count()

    for offset in range(0, total, batch_size):
        batch = articles[offset:offset + batch_size]
        batch_ids = list(batch.values_list('id', flat=True))

        Article.objects.filter(id__in=batch_ids).update(status='draft')

        print(f"Processed {min(offset + batch_size, total)}/{total}")

class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(migrate_large_table, migrations.RunPython.noop),
    ]
```

### Conditional Data Migration

```python
def create_profiles(apps, schema_editor):
    """Create profiles for users who don't have one"""
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('myapp', 'Profile')

    for user in User.objects.filter(is_active=True):
        Profile.objects.get_or_create(
            user=user,
            defaults={'bio': '', 'notification_enabled': True}
        )

class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0005_profile'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_profiles, migrations.RunPython.noop),
    ]
```

## Migration Conflicts

### Detecting and Resolving

```bash
# Check for conflicts
python manage.py migrate --check

# Auto-merge (when safe)
python manage.py makemigrations --merge

# Show migration plan
python manage.py showmigrations --plan
```

### Merge Migration

```python
class Migration(migrations.Migration):
    """Merge migration for parallel branches"""

    dependencies = [
        ('myapp', '0004_add_status'),    # Branch A
        ('myapp', '0004_add_category'),  # Branch B
    ]

    operations = [
        # Empty if branches don't conflict
        # Django marks both as applied
    ]
```

## Rollback Strategies

### Rolling Back

```bash
# Rollback to specific migration
python manage.py migrate myapp 0003

# Rollback all migrations
python manage.py migrate myapp zero

# Show rollback plan
python manage.py migrate myapp 0003 --plan
```

### Reversible Data Migrations

```python
def forward(apps, schema_editor):
    """Convert codes to strings"""
    Article = apps.get_model('myapp', 'Article')

    mapping = {'P': 'published', 'D': 'draft', 'A': 'archived'}
    for old, new in mapping.items():
        Article.objects.filter(status_code=old).update(status=new)

def reverse(apps, schema_editor):
    """Convert strings back to codes"""
    Article = apps.get_model('myapp', 'Article')

    mapping = {'published': 'P', 'draft': 'D', 'archived': 'A'}
    for old, new in mapping.items():
        Article.objects.filter(status=old).update(status_code=new)

class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(forward, reverse),
    ]
```

## Best Practices

### 1. Always Test Migrations First

```bash
# Test locally on production snapshot
python manage.py migrate --plan  # Review
python manage.py migrate         # Apply
python manage.py migrate myapp 0003  # Test rollback
python manage.py migrate myapp 0004  # Re-apply
```

### 2. Backup Before Major Migrations

```bash
# PostgreSQL
pg_dump dbname > backup_$(date +%Y%m%d).sql

# MySQL
mysqldump -u user -p dbname > backup_$(date +%Y%m%d).sql

# SQLite
cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d)
```

### 3. Use Transactions (Default)

```python
class Migration(migrations.Migration):
    atomic = True  # Default - rollback on error

    operations = [...]

# Disable only when required (e.g., CONCURRENT indexes)
class Migration(migrations.Migration):
    atomic = False
```

### 4. Separate Schema and Data Migrations

```python
# Migration 0005: Schema change
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(model_name='article', name='status', ...),
    ]

# Migration 0006: Data migration
class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(populate_status, reverse_populate_status),
    ]

# Easier to test and rollback separately
```

### 5. Document Complex Migrations

```python
class Migration(migrations.Migration):
    """
    Migrate article status from codes to strings.

    Changes:
    1. Adds 'status' CharField
    2. Converts codes: P->published, D->draft, A->archived
    3. Removes 'status_code' field

    Rollback: Converts strings back to codes
    Safe to re-run: Yes (idempotent)
    Estimated time: ~2 min for 100K articles
    """

    operations = [...]
```

### 6. Handle Large Tables Carefully

```python
# Process in batches
def migrate_in_batches(apps, schema_editor):
    Model = apps.get_model('myapp', 'Model')

    batch_size = 5000
    queryset = Model.objects.filter(needs_update=True)

    while queryset.exists():
        batch_ids = list(queryset[:batch_size].values_list('id', flat=True))
        Model.objects.filter(id__in=batch_ids).update(field='value')
```

### 7. Use Constraints for Data Integrity

```python
# Add constraints to prevent bad data
migrations.AddConstraint(
    model_name='article',
    constraint=models.CheckConstraint(
        check=models.Q(views__gte=0),
        name='views_non_negative'
    ),
)

migrations.AddConstraint(
    model_name='article',
    constraint=models.UniqueConstraint(
        fields=['author', 'slug'],
        name='unique_author_slug'
    ),
)
```

## Common Pitfalls

### ❌ Changing Field Type Without Data Migration

```python
# BAD: Direct type change loses data
migrations.AlterField(
    model_name='article',
    name='price',
    field=models.DecimalField(max_digits=10, decimal_places=2),
)
# If price was CharField, data conversion may fail!

# GOOD: Three-step migration
# 1. Add new field
# 2. Copy and convert data
# 3. Remove old field, rename new field
```

### ❌ Non-Atomic Operations Without atomic=False

```python
# BAD: CONCURRENT index without atomic=False
class Migration(migrations.Migration):
    operations = [
        AddIndexConcurrently(...)  # Fails!
    ]

# GOOD: Set atomic=False
class Migration(migrations.Migration):
    atomic = False
    operations = [
        AddIndexConcurrently(...)
    ]
```

### ❌ Referencing Models Directly

```python
# BAD: Direct model import
from myapp.models import Article

def migrate_data(apps, schema_editor):
    for article in Article.objects.all():  # Wrong!
        pass

# GOOD: Use apps.get_model()
def migrate_data(apps, schema_editor):
    Article = apps.get_model('myapp', 'Article')
    for article in Article.objects.all():  # Correct!
        pass
```

### ❌ Not Testing Rollback

```python
# Always provide reverse migration or use noop
migrations.RunPython(
    forward_func,
    migrations.RunPython.noop  # If can't reverse
)

# Better: Provide actual reverse
migrations.RunPython(forward_func, reverse_func)
```

## Emergency Procedures

### Mark Migration as Applied (Use with Caution)

```bash
# If migration already applied manually
python manage.py migrate --fake myapp 0005

# Fake to specific migration
python manage.py migrate --fake myapp 0003
```

### Squash Migrations (Cleanup)

```bash
# Combine migrations 0001-0010 into one
python manage.py squashmigrations myapp 0001 0010

# Useful after many development migrations
# Test thoroughly before deploying!
```
