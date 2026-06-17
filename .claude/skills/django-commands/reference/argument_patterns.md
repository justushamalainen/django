# Argument Patterns Reference

## Quick Reference

| Pattern | Example |
|---------|---------|
| Positional | `parser.add_argument('username', type=str)` |
| Flag | `parser.add_argument('--dry-run', action='store_true')` |
| Optional with value | `parser.add_argument('--limit', type=int, default=100)` |
| Short form | `parser.add_argument('-v', '--verbose', action='store_true')` |
| Choices | `parser.add_argument('--format', choices=['json', 'csv'])` |
| Multiple values | `parser.add_argument('files', nargs='+')` |
| Mutually exclusive | `group = parser.add_mutually_exclusive_group()` |

## nargs Values

| Value | Description |
|-------|-------------|
| `N` (int) | Exactly N arguments |
| `'?'` | 0 or 1 argument |
| `'*'` | 0 or more arguments |
| `'+'` | 1 or more arguments |

## Custom Validator Example

```python
def valid_date(date_string):
    from datetime import datetime
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        raise argparse.ArgumentTypeError(f'Invalid date: {date_string}')

parser.add_argument('--start-date', type=valid_date)
```
