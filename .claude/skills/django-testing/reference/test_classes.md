# Django Test Classes - Quick Reference

## Decision Tree

```
Need database?
├─ NO → SimpleTestCase
└─ YES → Testing transaction.atomic()?
    ├─ NO → TestCase (use this 99% of the time)
    └─ YES → TransactionTestCase
```

## Performance

| Class | Speed | Use Case |
|-------|-------|----------|
| SimpleTestCase | ⚡⚡⚡ | URLs, forms, utilities (no DB) |
| TestCase | ⚡⚡ | Standard tests (99% of cases) |
| TransactionTestCase | ⚡ | Transaction behavior (rare) |

**Key:** TestCase wraps each test in a transaction (fast). TransactionTestCase truncates tables (slow).
