# Django URL Patterns Reference

## Path Converters

| Converter | Matches | Returns |
|-----------|---------|---------|
| `<str:name>` | Any non-empty string (no `/`) | String |
| `<int:pk>` | Zero or positive integer | Integer |
| `<slug:slug>` | ASCII letters, numbers, `-`, `_` | String |
| `<uuid:id>` | UUID format | UUID object |
| `<path:file_path>` | Any string (includes `/`) | String |

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

```python
from django.urls import reverse, reverse_lazy

# In views
url = reverse('article-detail', kwargs={'pk': 1})
url = reverse('blog:article-detail', kwargs={'pk': 1})  # With namespace

# In models - for CreateView/UpdateView success redirect
class Article(models.Model):
    def get_absolute_url(self):
        return reverse('article-detail', kwargs={'pk': self.pk})

# In CBV class attributes - use reverse_lazy (URLs not loaded yet)
class ArticleCreateView(CreateView):
    success_url = reverse_lazy('article-list')
```

```django
{# In templates #}
<a href="{% url 'article-detail' pk=article.pk %}">Read More</a>
<a href="{% url 'blog:article-detail' pk=article.pk %}">With namespace</a>
```

## Django-Specific Gotchas

**URL order matters:** Specific patterns before general

```python
urlpatterns = [
    path('articles/featured/', views.featured),  # Specific first
    path('articles/<slug:slug>/', views.detail),  # General last
]
```

**Naming convention:** Use `model-action` format

```python
urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article-list'),
    path('<int:pk>/', views.ArticleDetailView.as_view(), name='article-detail'),
    path('create/', views.ArticleCreateView.as_view(), name='article-create'),
]
```
