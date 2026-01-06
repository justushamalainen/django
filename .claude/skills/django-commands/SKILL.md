# Django Management Commands Skill

This skill helps you create Django management commands - custom scripts run with `python manage.py <command>`.

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

## Quick Start

Create a command in 3 steps:

1. **Create the file structure:**
   ```bash
   mkdir -p myapp/management/commands
   touch myapp/management/commands/__init__.py
   touch myapp/management/commands/mycommand.py
   ```

2. **Write the command:**
   ```python
   from django.core.management.base import BaseCommand

   class Command(BaseCommand):
       help = 'Description of what this command does'

       def handle(self, *args, **options):
           self.stdout.write(self.style.SUCCESS('Command executed successfully'))
   ```

3. **Run it:**
   ```bash
   python manage.py mycommand
   ```

## Core Concepts

### Command Structure

Every command needs:
- `Command` class inheriting from `BaseCommand`
- `help` attribute describing the command
- `handle()` method with your logic

```python
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Process user data'

    def handle(self, *args, **options):
        # Your command logic here
        self.stdout.write('Processing...')
```

### Adding Arguments

Override `add_arguments()` to accept input:

```python
def add_arguments(self, parser):
    # Positional argument
    parser.add_argument('username', type=str, help='Username to process')

    # Optional flag
    parser.add_argument('--dry-run', action='store_true', help='Preview changes')

    # Optional with value
    parser.add_argument('--limit', type=int, default=100, help='Max items')

def handle(self, *args, **options):
    username = options['username']
    dry_run = options['dry_run']
    limit = options['limit']
```

See [reference/argument_patterns.md](reference/argument_patterns.md) for more argument patterns.

### Output Styling

Use built-in styles for consistent, colored output:

```python
self.stdout.write(self.style.SUCCESS('Operation completed'))
self.stdout.write(self.style.ERROR('Operation failed'))
self.stdout.write(self.style.WARNING('Deprecation warning'))
self.stdout.write(self.style.NOTICE('FYI: something changed'))
```

### Error Handling

Raise `CommandError` for user-facing errors:

```python
from django.core.management.base import CommandError

def handle(self, *args, **options):
    try:
        obj = MyModel.objects.get(id=options['id'])
    except MyModel.DoesNotExist:
        raise CommandError(f'MyModel with id {options["id"]} does not exist')
```

## Complete Example

```python
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import csv

class Command(BaseCommand):
    help = 'Import users from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='CSV file path')
        parser.add_argument('--batch-size', type=int, default=1000)
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        # Validate
        if not os.path.isfile(options['file']):
            raise CommandError(f'File not found: {options["file"]}')

        # Process in batches with transaction
        batch = []
        with open(options['file'], 'r') as f:
            for row in csv.DictReader(f):
                batch.append(User(username=row['username'], email=row['email']))

                if len(batch) >= options['batch_size']:
                    if not options['dry_run']:
                        with transaction.atomic():
                            User.objects.bulk_create(batch)
                    self.stdout.write(f'Processed {len(batch)} users')
                    batch = []

        self.stdout.write(self.style.SUCCESS('Import complete'))
```

## Best Practices & Patterns

**Essential practices:**
- Always implement `--dry-run` for destructive operations
- Use `transaction.atomic()` to wrap related DB operations
- Use `.iterator(chunk_size=2000)` for large querysets
- Validate inputs early and raise `CommandError` for user errors
- Use `self.style.SUCCESS/ERROR/WARNING` for output

**Common patterns:**
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

## Troubleshooting

**Command Not Found:**
- Verify directory structure: `myapp/management/commands/mycommand.py`
- Check `__init__.py` files exist in `management/` and `commands/`
- Ensure app is in `INSTALLED_APPS`

**AppRegistryNotReady:**
- Don't import models at module level
- Import models inside `handle()` method if needed

## References

- [reference/argument_patterns.md](reference/argument_patterns.md) - Argument types and examples
- Django docs: https://docs.djangoproject.com/en/stable/howto/custom-management-commands/
