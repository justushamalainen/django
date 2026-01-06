# Django Views & URL Routing Skill

## Overview

This skill helps you build Django views (function-based and class-based) and configure URL routing efficiently.

**Use this skill when you need to:**
- Create CRUD operations
- Choose between FBV and CBV
- Configure URL patterns
- Apply view decorators

## FBV vs CBV Decision

```
Need to handle HTTP request?
│
├─ Simple logic, one-time use? → FBV
│  └─ API endpoint, redirect, form handler
│
├─ CRUD operations? → CBV
│  └─ ListView, DetailView, CreateView, UpdateView, DeleteView
│
├─ Reusable behavior? → CBV with mixins
│  └─ LoginRequiredMixin, PermissionRequiredMixin
│
└─ Complex business logic? → FBV
   └─ CBVs can become hard to follow
```

**FBV:** Explicit, easier to debug, simpler
**CBV:** Code reuse, DRY for CRUD, built-in pagination

## Common Generic Views

### ListView

```python
from django.views.generic import ListView

class ArticleListView(ListView):
    model = Article
    template_name = 'blog/article_list.html'
    paginate_by = 20

    def get_queryset(self):
        return Article.objects.select_related('author').filter(
            published=True
        ).order_by('-created_at')
```

### DetailView

```python
from django.views.generic import DetailView

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blog/article_detail.html'
    slug_field = 'slug'

    def get_queryset(self):
        return super().get_queryset().select_related('author')
```

### CreateView

```python
from django.views.generic import CreateView
from django.urls import reverse_lazy

class ArticleCreateView(CreateView):
    model = Article
    fields = ['title', 'content']
    template_name = 'blog/article_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
```

### UpdateView

```python
from django.views.generic import UpdateView

class ArticleUpdateView(UpdateView):
    model = Article
    fields = ['title', 'content']
    template_name = 'blog/article_form.html'

    def get_queryset(self):
        # Only allow editing own articles
        return Article.objects.filter(author=self.request.user)
```

### DeleteView

```python
from django.views.generic import DeleteView
from django.urls import reverse_lazy

class ArticleDeleteView(DeleteView):
    model = Article
    template_name = 'blog/article_confirm_delete.html'
    success_url = reverse_lazy('article-list')
```

## URL Configuration

### Basic Patterns

```python
from django.urls import path
from . import views

urlpatterns = [
    path('articles/', views.ArticleListView.as_view(), name='article-list'),
    path('articles/<int:pk>/', views.ArticleDetailView.as_view(), name='article-detail'),
    path('articles/create/', views.ArticleCreateView.as_view(), name='article-create'),
    path('articles/<int:pk>/edit/', views.ArticleUpdateView.as_view(), name='article-update'),
    path('articles/<int:pk>/delete/', views.ArticleDeleteView.as_view(), name='article-delete'),
]
```

### With Namespace

```python
# Project urls.py
urlpatterns = [
    path('blog/', include('blog.urls', namespace='blog')),
]

# blog/urls.py
app_name = 'blog'
urlpatterns = [
    path('', views.ArticleListView.as_view(), name='list'),
]

# Usage
reverse('blog:list')  # → /blog/
{% url 'blog:list' %}
```

## Decorator Patterns

### Require Login (FBV)

```python
from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    return render(request, 'profile.html')
```

### Require HTTP Methods

```python
from django.views.decorators.http import require_http_methods, require_GET, require_POST

@require_http_methods(["GET", "POST"])
def article_form(request):
    if request.method == 'POST':
        # Handle form
        pass
    return render(request, 'form.html')

@require_GET
def article_list(request):
    articles = Article.objects.all()
    return render(request, 'list.html', {'articles': articles})

@require_POST
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.delete()
    return redirect('article-list')
```

### Access Control with CBV

```python
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    fields = ['title', 'content']

    def test_func(self):
        return self.get_object().author == self.request.user
```

## Common Patterns

### JSON Response

```python
from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def article_api(request):
    articles = Article.objects.filter(published=True)
    return JsonResponse({
        'count': articles.count(),
        'results': [{'id': a.id, 'title': a.title} for a in articles]
    })
```

### File Download

```python
from django.http import FileResponse
from django.contrib.auth.decorators import login_required

@login_required
def download_file(request, pk):
    report = get_object_or_404(Report, pk=pk, user=request.user)
    return FileResponse(
        report.file.open('rb'),
        as_attachment=True,
        filename=report.file.name
    )
```

## Security Essentials

### CSRF Protection

```python
# All POST/PUT/DELETE need CSRF token
# In template:
{% csrf_token %}

# For APIs with token auth only:
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Only use with proper token auth
def api_endpoint(request):
    pass
```

### Avoid N+1 Queries

```python
# BAD
articles = Article.objects.all()  # Template: {{ article.author.name }} → N+1

# GOOD
articles = Article.objects.select_related('author').all()
```

## Reference Files

- **`reference/cbv_mixins.md`** - Mixin decision matrix and patterns
- **`reference/url_patterns.md`** - URL routing and reversing

## Troubleshooting

**CSRF verification failed:**
- Ensure `{% csrf_token %}` in forms
- Check `CSRF_TRUSTED_ORIGINS` in settings

**Page not found (404):**
- Check URL pattern order (specific before generic)
- Verify namespace with `app_name`

**Slow performance:**
- Use `django-debug-toolbar`
- Add `select_related()` / `prefetch_related()`
