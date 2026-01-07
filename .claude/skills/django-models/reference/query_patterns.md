# Django Query Patterns - Essential 5

## 1. select_related (SQL JOIN)

Use for ForeignKey and OneToOne (forward direction)

```python
# BAD: N+1 queries
for article in Article.objects.all():
    print(article.author.name)  # N queries

# GOOD: 1 query with JOIN
articles = Article.objects.select_related('author')
articles = Article.objects.select_related('author', 'category')  # Multiple
articles = Article.objects.select_related('author__profile')  # Chained
```

## 2. prefetch_related (Separate Queries)

Use for ManyToMany and reverse ForeignKey

```python
# BAD: N+1 queries
for article in Article.objects.all():
    tags = article.tags.all()  # N queries

# GOOD: 2 queries (one for articles, one for tags with IN clause)
articles = Article.objects.prefetch_related('tags')
articles = Article.objects.prefetch_related('comments__author')  # Nested

# Combine with select_related
articles = Article.objects.select_related('author').prefetch_related('tags')
```

Custom prefetch with filters:
```python
from django.db.models import Prefetch

articles = Article.objects.prefetch_related(
    Prefetch(
        'comments',
        queryset=Comment.objects.filter(approved=True),
        to_attr='approved_comments'
    )
)
```

## 3. Q Objects (Complex Queries)

```python
from django.db.models import Q

# OR, NOT, complex logic
Article.objects.filter(Q(status='published') | Q(status='archived'))
Article.objects.filter(~Q(status='draft'))
Article.objects.filter(Q(status='published') & (Q(featured=True) | Q(views__gte=1000)))

# Dynamic query building
filters = Q()
if title:
    filters &= Q(title__icontains=title)
Article.objects.filter(filters)

# Search multiple fields
Article.objects.filter(
    Q(title__icontains=query) | Q(content__icontains=query)
)
```

## 4. F Expressions (Field References)

```python
from django.db.models import F

# Compare fields
Article.objects.filter(views__gt=F('likes'))

# Atomic increment (prevents race conditions)
Article.objects.filter(pk=id).update(views=F('views') + 1)

# Arithmetic
Article.objects.filter(updated_at__gt=F('created_at') + timedelta(days=7))
Article.objects.order_by(F('views') + F('likes'))

# With annotations
Article.objects.annotate(
    popularity=F('views') + F('likes') * 2
).order_by('-popularity')
```

## 5. Annotations (Calculated Fields)

```python
from django.db.models import Count, Avg, Sum, Max, Min

# Count related objects and filter on annotation
authors = Author.objects.annotate(book_count=Count('books')).filter(book_count__gte=5)

# Multiple annotations
articles = Article.objects.annotate(
    comment_count=Count('comments'),
    avg_rating=Avg('ratings__score')
)

# Conditional aggregation
articles = Article.objects.annotate(
    approved=Count('comments', filter=Q(comments__approved=True))
)

# Case/When for priority
from django.db.models import Case, When, Value

articles = Article.objects.annotate(
    priority=Case(
        When(featured=True, then=Value(1)),
        When(views__gte=1000, then=Value(2)),
        default=Value(3)
    )
).order_by('priority')

# Calculations
Order.objects.annotate(total=Sum(F('quantity') * F('price')))
```

## Quick Reference Table

| Pattern | Use Case | Example |
|---------|----------|---------|
| **select_related** | ForeignKey, OneToOne | `.select_related('author')` |
| **prefetch_related** | ManyToMany, reverse FK | `.prefetch_related('tags')` |
| **Q objects** | OR, NOT, complex logic | `Q(a=1) \| Q(b=2)` |
| **F expressions** | Field comparisons, atomic updates | `.update(views=F('views')+1)` |
| **Annotations** | Count, Sum, Avg, calculated fields | `.annotate(count=Count('items'))` |

## Quick Optimization Tips

```python
# Use exists() not count() for boolean checks
if Article.objects.filter(status='published').exists():

# Use count() not len() for counting
count = Article.objects.count()  # Not len(Article.objects.all())

# Bulk updates
Article.objects.filter(id__in=ids).update(views=F('views') + 1)

# Defer large fields
articles = Article.objects.defer('content', 'description')
articles = Article.objects.only('id', 'title', 'status')
```
