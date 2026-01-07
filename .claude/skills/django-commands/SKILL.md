# Django Management Commands Skill

## When to Use

**Use management commands for:**
- Database operations requiring Django ORM
- Commands run via cron, systemd, or CI/CD
- Batch processing with progress reporting
- Data import/export and maintenance tasks

**Don't use when:**
- A simple Python script would suffice
- You need real-time request handling (use views)
- Celery/background tasks are more appropriate

## Django-Specific Structure

**File location:** `myapp/management/commands/mycommand.py`

```python
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Command description'

    def add_arguments(self, parser):
        # Override to accept arguments
        parser.add_argument('username', type=str)
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        # Access arguments via options dict
        username = options['username']
        self.stdout.write('Processing...')
```

See [reference/argument_patterns.md](reference/argument_patterns.md) for argument patterns.

## Django-Specific Patterns

**Output styling:**
```python
self.stdout.write(self.style.SUCCESS('Operation completed'))
self.stdout.write(self.style.ERROR('Operation failed'))
self.stdout.write(self.style.WARNING('Deprecation warning'))
```

**Error handling:**
```python
from django.core.management.base import CommandError

raise CommandError(f'MyModel with id {id} does not exist')
```

**Django best practices:**
- Implement `--dry-run` for destructive operations
- Use `transaction.atomic()` for related DB operations
- Use `.iterator(chunk_size=2000)` for large querysets
- Validate inputs early, raise `CommandError` for user errors

```python
# Transaction pattern
with transaction.atomic():
    MyModel.objects.filter(status='old').update(status='archived')

# Iterator pattern for memory efficiency
for item in MyModel.objects.all().iterator(chunk_size=2000):
    process(item)

# Dry-run pattern
if options['dry_run']:
    self.stdout.write(f'Would delete {count} items')
else:
    items.delete()
```

## Django-Specific Troubleshooting

**Command Not Found:** Check `__init__.py` exists in `management/` and `commands/` dirs, app in `INSTALLED_APPS`

**AppRegistryNotReady:** Import models inside `handle()` method, not at module level
