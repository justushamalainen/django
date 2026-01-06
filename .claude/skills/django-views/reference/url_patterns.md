# Django URL Patterns Reference

## Path Basics

### Simple URL Patterns

```python
from django.urls import path
from . import views

urlpatterns = [
    # Static paths
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # With parameters
    path('articles/<int:pk>/', views.article_detail, name='article-detail'),
    path('category/<slug:slug>/', views.category, name='category'),
    path('archive/<int:year>/<int:month>/', views.archive, name='archive'),
]
```

## Built-in Path Converters

| Converter | Matches | Returns | Example |
|-----------|---------|---------|---------|
| `str` | Any non-empty string (no `/`) | String | `<str:name>` |
| `int` | Zero or positive integer | Integer | `<int:pk>` |
| `slug` | ASCII letters, numbers, `-`, `_` | String | `<slug:slug>` |
| `uuid` | UUID format | UUID object | `<uuid:id>` |
| `path` | Any string (includes `/`) | String | `<path:file_path>` |

### Examples

```python
path('article/<int:pk>/', views.article_detail)
# Matches: /article/1/, /article/999/

path('post/<slug:slug>/', views.post_detail)
# Matches: /post/my-first-post/, /post/hello_world/

path('file/<path:file_path>/', views.serve_file)
# Matches: /file/docs/guide.pdf, /file/a/b/c/d.txt
```

## URL Namespacing

### Application Namespace

**Project urls.py:**
```python
from django.urls import path, include

urlpatterns = [
    path('blog/', include('blog.urls', namespace='blog')),
    path('shop/', include('shop.urls', namespace='shop')),
]
```

**App urls.py (blog/urls.py):**
```python
from django.urls import path
from . import views

app_name = 'blog'  # REQUIRED for namespace

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='list'),
    path('<int:pk>/', views.ArticleDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ArticleUpdateView.as_view(), name='edit'),
]
```

## URL Reversing

### In Views

```python
from django.urls import reverse
from django.shortcuts import redirect

# Basic
url = reverse('article-detail', kwargs={'pk': 1})
# → /articles/1/

# With namespace
url = reverse('blog:article-detail', kwargs={'pk': 1})

# Redirect
return redirect('article-detail', pk=1)
```

### In Templates

```django
{# Basic #}
<a href="{% url 'article-detail' pk=article.pk %}">Read More</a>

{# With namespace #}
<a href="{% url 'blog:article-detail' pk=article.pk %}">Read More</a>

{# Positional args #}
<a href="{% url 'archive' 2024 1 %}">January 2024</a>
```

### In Models

```python
from django.urls import reverse

class Article(models.Model):
    title = models.CharField(max_length=200)

    def get_absolute_url(self):
        """Used by CreateView, UpdateView success redirect."""
        return reverse('article-detail', kwargs={'pk': self.pk})
```

### reverse_lazy for Class Attributes

```python
from django.urls import reverse_lazy
from django.views.generic import CreateView

class ArticleCreateView(CreateView):
    model = Article
    success_url = reverse_lazy('article-list')
    # reverse() would fail here - URLs not loaded yet!
```

## Best Practices

### 1. Always Name Your URLs

```python
# GOOD
path('articles/', views.list, name='article-list')

# BAD
path('articles/', views.list)
```

### 2. Use Consistent Naming Convention

```python
# Convention: model-action
urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article-list'),
    path('<int:pk>/', views.ArticleDetailView.as_view(), name='article-detail'),
    path('create/', views.ArticleCreateView.as_view(), name='article-create'),
    path('<int:pk>/edit/', views.ArticleUpdateView.as_view(), name='article-update'),
    path('<int:pk>/delete/', views.ArticleDeleteView.as_view(), name='article-delete'),
]
```

### 3. Use Namespaces for Apps

```python
# GOOD - Clear, no conflicts
reverse('blog:article-detail', kwargs={'pk': 1})
reverse('shop:product-detail', kwargs={'pk': 1})

# BAD - Name collisions possible
reverse('article-detail', kwargs={'pk': 1})
```

### 4. Order URLs Specific to General

```python
urlpatterns = [
    # Specific patterns first
    path('articles/featured/', views.featured),
    path('articles/latest/', views.latest),

    # General patterns last
    path('articles/<slug:slug>/', views.detail),
]
```

### 5. Avoid Hardcoded URLs

```python
# BAD
return redirect('/articles/1/')

# GOOD
return redirect('article-detail', pk=1)
```
