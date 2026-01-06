# Command Argument Patterns

Quick reference for adding arguments to Django management commands using `argparse`.

## Basic Syntax

```python
def add_arguments(self, parser):
    parser.add_argument('name', type=str, help='Item name')
    parser.add_argument('--verbose', action='store_true')

def handle(self, *args, **options):
    name = options['name']
    verbose = options['verbose']
```

## Positional Arguments

```python
# Single required argument
parser.add_argument('username', type=str, help='Username to process')

# Multiple required arguments
parser.add_argument('source', type=str, help='Source file')
parser.add_argument('destination', type=str, help='Destination file')

# One or more arguments (list)
parser.add_argument('files', nargs='+', type=str, help='Files to process')

# Zero or more arguments (optional list)
parser.add_argument('files', nargs='*', type=str, help='Optional files')
```

## Optional Arguments

```python
# Boolean flag
parser.add_argument('--dry-run', action='store_true', help='Preview changes')

# Inverse boolean flag (True by default, False when flag is used)
parser.add_argument('--no-backup', action='store_false', dest='backup')

# Optional with value
parser.add_argument('--limit', type=int, default=100, help='Max items')

# Required optional argument
parser.add_argument('--config', type=str, required=True, help='Config file')

# Short and long forms
parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
```

## Argument Types

```python
# Built-in types
parser.add_argument('--count', type=int)
parser.add_argument('--price', type=float)
parser.add_argument('--name', type=str)  # Default type

# Choices (enum)
parser.add_argument('--format', choices=['json', 'csv', 'xml'], default='json')

# Custom validator
def valid_date(date_string):
    from datetime import datetime
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        raise argparse.ArgumentTypeError(f'Invalid date: {date_string}. Use YYYY-MM-DD')

parser.add_argument('--start-date', type=valid_date, help='Start date (YYYY-MM-DD)')
```

## Advanced Patterns

```python
# Mutually exclusive options
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--create', action='store_true')
group.add_argument('--update', action='store_true')
group.add_argument('--delete', action='store_true')

# Argument groups (visual organization)
input_group = parser.add_argument_group('input options')
input_group.add_argument('--input', type=str)
input_group.add_argument('--format', choices=['json', 'csv'])

# Append action (build list from multiple uses)
parser.add_argument('--include', action='append', help='Include pattern')
# Usage: --include "*.py" --include "*.js"
# Result: options['include'] = ['*.py', '*.js']

# Count action (increment for multiple uses)
parser.add_argument('-v', '--verbose', action='count', default=0)
# Usage: -vvv gives verbosity = 3
```

## nargs Values

| Value | Description | Example |
|-------|-------------|---------|
| `N` (int) | Exactly N arguments | `nargs=2` |
| `'?'` | 0 or 1 argument | Optional single arg |
| `'*'` | 0 or more arguments | Optional list |
| `'+'` | 1 or more arguments | Required list |

## Complete Example

```python
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Import data from files'

    def add_arguments(self, parser):
        # Positional: files
        parser.add_argument('files', nargs='+', type=str, help='Input files')

        # Format options
        parser.add_argument('--format', choices=['json', 'csv'], help='File format')
        parser.add_argument('--batch-size', type=int, default=1000, help='Batch size')

        # Flags
        parser.add_argument('--dry-run', action='store_true', help='Preview only')
        parser.add_argument('--skip-errors', action='store_true', help='Continue on errors')

        # Verbosity
        parser.add_argument('-v', '--verbose', action='count', default=0)

    def handle(self, *args, **options):
        files = options['files']
        batch_size = options['batch_size']

        # Validate
        if batch_size < 1 or batch_size > 10000:
            raise CommandError('Batch size must be between 1 and 10000')

        # Process
        for file_path in files:
            if options['verbose'] >= 1:
                self.stdout.write(f'Processing {file_path}')
```
