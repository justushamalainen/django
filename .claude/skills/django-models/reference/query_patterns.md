# Django Query Patterns - Essential 5

The 5 most common query optimization patterns Django developers use daily.

## 1. select_related (SQL JOIN)

**Use for:** Forward ForeignKey and OneToOne relationships

**How it works:** Creates SQL JOIN, returns objects in single query

```python
# BAD: N+1 queries
articles = Article.objects.all()  # 1 query
for article in articles:
    print(article.author.name)    # N queries (one per article)

# GOOD: 1 query with JOIN
articles = Article.objects.select_related('author')
for article in articles:
    print(article.author.name)    # No extra queries

# Multiple relationships
articles = Article.objects.select_related('author', 'category')

# Chained relationships
articles = Article.objects.select_related('author__profile')
```

**When to use:**
- ForeignKey (forward direction)
- OneToOneField
- When you need the related data

**When NOT to use:**
- ManyToMany relationships (use prefetch_related)
- Reverse ForeignKey (use prefetch_related)

## 2. prefetch_related (Separate Queries)

**Use for:** Reverse ForeignKey, ManyToMany, and multiple related objects

**How it works:** Separate queries, joins in Python with IN clause

```python
# BAD: N+1 queries
articles = Article.objects.all()  # 1 query
for article in articles:
    tags = article.tags.all()     # N queries

# GOOD: 2 queries total
articles = Article.objects.prefetch_related('tags')
# Query 1: SELECT * FROM article
# Query 2: SELECT * FROM tag WHERE id IN (...)
for article in articles:
    tags = article.tags.all()     # No extra queries (cached)

# Multiple levels
articles = Article.objects.prefetch_related('comments__author')

# Combine with select_related
articles = Article.objects.select_related('author').prefetch_related('tags')
```

**Custom prefetch with filters:**
```python
from django.db.models import Prefetch

articles = Article.objects.prefetch_related(
    Prefetch(
        'comments',
        queryset=Comment.objects.filter(approved=True).select_related('author'),
        to_attr='approved_comments'
    )
)

# Access filtered results
for article in articles:
    for comment in article.approved_comments:
        print(comment.text)
```

**When to use:**
- ManyToManyField
- Reverse ForeignKey (author.books.all())
- GenericRelation
- When you need filtered related objects

## 3. Q Objects (Complex Queries)

**Use for:** OR conditions, NOT conditions, complex logic

```python
from django.db.models import Q

# OR conditions
Article.objects.filter(
    Q(status='published') | Q(status='archived')
)

# NOT conditions
Article.objects.filter(~Q(status='draft'))

# Complex nested logic
Article.objects.filter(
    Q(status='published') &
    (Q(featured=True) | Q(views__gte=1000))
)
# SQL: WHERE status='published' AND (featured=true OR views >= 1000)

# Dynamic query building
filters = Q()
if title:
    filters &= Q(title__icontains=title)
if author_name:
    filters &= Q(author__name__icontains=author_name)
if tags:
    filters &= Q(tags__name__in=tags)

articles = Article.objects.filter(filters)
```

**Common patterns:**
```python
# Multiple OR conditions
Article.objects.filter(
    Q(status='published') | Q(status='featured') | Q(views__gte=1000)
)

# Exclude with complex logic
Article.objects.filter(
    ~Q(status='draft') & ~Q(status='deleted')
)

# Search across multiple fields
Article.objects.filter(
    Q(title__icontains=query) |
    Q(content__icontains=query) |
    Q(author__name__icontains=query)
)
```

## 4. F Expressions (Field References)

**Use for:** Reference model fields in queries and atomic updates

```python
from django.db.models import F

# Compare two fields
Article.objects.filter(views__gt=F('likes'))

# Atomic increment (no race conditions)
Article.objects.filter(pk=article_id).update(views=F('views') + 1)

# Arithmetic in queries
from datetime import timedelta
Article.objects.filter(
    updated_at__gt=F('created_at') + timedelta(days=7)
)

# Order by calculated field
Article.objects.order_by(F('views') + F('likes'))

# Compare across relationships
Article.objects.filter(author__age__gt=F('reviewer__age'))
```

**With annotations:**
```python
from django.db.models import ExpressionWrapper, IntegerField

Article.objects.annotate(
    popularity=ExpressionWrapper(
        F('views') + F('likes') * 2,
        output_field=IntegerField()
    )
).order_by('-popularity')
```

**Why use F() for updates:**
```python
# BAD: Race condition
article = Article.objects.get(pk=1)
article.views = article.views + 1
article.save()

# GOOD: Atomic database-level update
Article.objects.filter(pk=1).update(views=F('views') + 1)
```

## 5. Annotations (Calculated Fields)

**Use for:** Add calculated fields to each object in queryset

```python
from django.db.models import Count, Avg, Sum, Max, Min

# Count related objects
authors = Author.objects.annotate(
    book_count=Count('books')
)
for author in authors:
    print(f"{author.name}: {author.book_count} books")

# Filter on annotation
popular_authors = Author.objects.annotate(
    book_count=Count('books')
).filter(book_count__gte=5)

# Multiple annotations
articles = Article.objects.annotate(
    comment_count=Count('comments'),
    avg_rating=Avg('ratings__score'),
    total_views=Sum('views')
)
```

**Conditional aggregation:**
```python
# Count only approved comments
articles = Article.objects.annotate(
    approved_comments=Count('comments', filter=Q(comments__approved=True)),
    pending_comments=Count('comments', filter=Q(comments__approved=False))
)
```

**With Case/When:**
```python
from django.db.models import Case, When, Value, IntegerField

articles = Article.objects.annotate(
    priority=Case(
        When(featured=True, then=Value(1)),
        When(views__gte=1000, then=Value(2)),
        When(status='published', then=Value(3)),
        default=Value(4),
        output_field=IntegerField()
    )
).order_by('priority')
```

**Common aggregations:**
```python
# Count distinct
Author.objects.annotate(unique_publishers=Count('books__publisher', distinct=True))

# Latest related object
from django.db.models import Max
Article.objects.annotate(latest_comment_date=Max('comments__created_at'))

# Sum with calculations
Order.objects.annotate(
    total=Sum(F('quantity') * F('price'), output_field=DecimalField())
)
```

## Quick Reference Table

| Pattern | Use Case | Example |
|---------|----------|---------|
| **select_related** | ForeignKey, OneToOne | `.select_related('author')` |
| **prefetch_related** | ManyToMany, reverse FK | `.prefetch_related('tags')` |
| **Q objects** | OR, NOT, complex logic | `Q(a=1) \| Q(b=2)` |
| **F expressions** | Field comparisons, atomic updates | `.update(views=F('views')+1)` |
| **Annotations** | Count, Sum, Avg, calculated fields | `.annotate(count=Count('items'))` |

## Common Optimization Checklist

1. **Avoid N+1 queries**
   ```python
   # Add select_related/prefetch_related before iterating
   articles = Article.objects.select_related('author').prefetch_related('tags')
   ```

2. **Use exists() for checks**
   ```python
   # BAD
   if Article.objects.filter(status='published').count() > 0:

   # GOOD
   if Article.objects.filter(status='published').exists():
   ```

3. **Use count() instead of len()**
   ```python
   # BAD: Loads all objects
   count = len(Article.objects.all())

   # GOOD: Database COUNT query
   count = Article.objects.count()
   ```

4. **Bulk operations**
   ```python
   # BAD: N queries
   for article in articles:
       article.views += 1
       article.save()

   # GOOD: 1 query
   Article.objects.filter(id__in=article_ids).update(views=F('views') + 1)
   ```

5. **only() and defer() for large fields**
   ```python
   # Don't load large content field
   articles = Article.objects.defer('content', 'description')

   # Load only specific fields
   articles = Article.objects.only('id', 'title', 'status')
   ```

## Debugging Queries

```python
# Print SQL
print(Article.objects.filter(status='published').query)

# Count queries
from django.db import connection, reset_queries
from django.conf import settings

settings.DEBUG = True
reset_queries()

# Your code here
articles = Article.objects.select_related('author').all()
list(articles)

print(f"Total queries: {len(connection.queries)}")
for query in connection.queries:
    print(query['sql'])
```
