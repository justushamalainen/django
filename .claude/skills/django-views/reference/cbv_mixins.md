# Django Class-Based View Mixins Reference

## Mixin Decision Matrix

### When to Use Which Mixin

| Need | Mixin | Import From |
|------|-------|-------------|
| Require login | `LoginRequiredMixin` | `django.contrib.auth.mixins` |
| Check permissions | `PermissionRequiredMixin` | `django.contrib.auth.mixins` |
| Custom access check | `UserPassesTestMixin` | `django.contrib.auth.mixins` |
| Work with single object | `SingleObjectMixin` | `django.views.generic.detail` |
| Work with object list | `MultipleObjectMixin` | `django.views.generic.list` |
| Render template | `TemplateResponseMixin` | `django.views.generic.base` |
| Handle forms | `FormMixin` | `django.views.generic.edit` |
| Handle model forms | `ModelFormMixin` | `django.views.generic.edit` |

## Common Generic Views

### Display Views

```python
from django.views.generic import ListView, DetailView

class ArticleListView(ListView):
    model = Article
    paginate_by = 20
    ordering = ['-created_at']

class ArticleDetailView(DetailView):
    model = Article
    slug_field = 'slug'
```

### Editing Views

```python
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

class ArticleCreateView(CreateView):
    model = Article
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class ArticleUpdateView(UpdateView):
    model = Article
    fields = ['title', 'content']

class ArticleDeleteView(DeleteView):
    model = Article
    success_url = reverse_lazy('article-list')
```

## Access Control Patterns

```python
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Order matters: Access checks before view logic."""
    model = Article
    fields = ['title', 'content']

    def test_func(self):
        # Only allow editing own articles
        return self.get_object().author == self.request.user
```

## Method Resolution Order (MRO)

**Critical rule:** Always put access mixins first (leftmost), generic view last (rightmost).

```python
# GOOD
class MyView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    pass

# BAD - Login check happens AFTER dispatch
class MyView(UpdateView, LoginRequiredMixin):
    pass
```

## Best Practices

1. **Always call super()** in overridden methods to continue the mixin chain
2. **Put access mixins first** in the inheritance list
3. **Generic view goes last** in the inheritance list
4. **Keep mixins focused** - single responsibility
5. **Test MRO** when debugging: `print(MyView.__mro__)`
