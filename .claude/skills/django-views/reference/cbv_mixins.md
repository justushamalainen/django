# Django Class-Based View Mixins Reference

## Mixin Quick Reference

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

## Mixin Composition

**Critical:** Access mixins first (leftmost), generic view last (rightmost).

```python
# GOOD - Access checks before dispatch
class MyView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    pass

# BAD - Login check happens AFTER dispatch
class MyView(UpdateView, LoginRequiredMixin):
    pass
```

**Tips:**
- Always call `super()` in overridden methods
- Debug MRO with: `print(MyView.__mro__)`
