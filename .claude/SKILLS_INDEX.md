# Django Skills Index

Find the right skill for your task.

## Quick Reference

| Skill | Primary Use Cases |
|-------|-------------------|
| django-models | Data modeling, ORM, migrations |
| django-forms | Form creation, validation, widgets |
| django-views | Request handling, FBV/CBV |
| django-admin | Admin customization, actions |
| django-templates | Template rendering, tags, filters |
| django-testing | Unit tests, mocking, fixtures |
| django-commands | Management commands |

## Find Skills by Task

### "I need to..."

#### Data & Models
- **Create a model** → [django-models](skills/django-models/SKILL.md)
- **Add a field to existing model** → [django-models](skills/django-models/SKILL.md)
- **Write complex queries** → [django-models](skills/django-models/SKILL.md) (reference: query_patterns.md)
- **Debug slow queries / N+1** → [django-models](skills/django-models/SKILL.md)
- **Handle migrations** → [django-models](skills/django-models/SKILL.md) (reference: migration_ops.md)

#### Forms & Validation
- **Create a form** → [django-forms](skills/django-forms/SKILL.md)
- **Add custom validation** → [django-forms](skills/django-forms/SKILL.md) (reference: validation.md)
- **Customize widgets** → [django-forms](skills/django-forms/SKILL.md) (reference: widgets.md)

#### Views & URLs
- **Create a view** → [django-views](skills/django-views/SKILL.md)
- **Choose FBV vs CBV** → [django-views](skills/django-views/SKILL.md)
- **Configure URLs** → [django-views](skills/django-views/SKILL.md) (reference: url_patterns.md)

#### Templates
- **Create template** → [django-templates](skills/django-templates/SKILL.md)
- **Use template inheritance** → [django-templates](skills/django-templates/SKILL.md)
- **Use built-in tags/filters** → [django-templates](skills/django-templates/SKILL.md) (reference files)

#### Admin Interface
- **Customize admin** → [django-admin](skills/django-admin/SKILL.md)
- **Create custom actions** → [django-admin](skills/django-admin/SKILL.md) (reference: actions.md)
- **Add custom filters** → [django-admin](skills/django-admin/SKILL.md) (reference: filters.md)

#### Testing
- **Write unit tests** → [django-testing](skills/django-testing/SKILL.md)
- **Mock external services** → [django-testing](skills/django-testing/SKILL.md) (reference: mocking.md)
- **Choose test class** → [django-testing](skills/django-testing/SKILL.md) (reference: test_classes.md)

#### Commands
- **Create management command** → [django-commands](skills/django-commands/SKILL.md)
- **Add command arguments** → [django-commands](skills/django-commands/SKILL.md) (reference: argument_patterns.md)

## Skill Dependencies

```
django-models (foundation)
    ↓
django-forms (ModelForm)
    ↓
django-views (form processing)
    ↓
django-templates (rendering)

django-admin ← django-models
django-testing (cross-cutting)
django-commands ← django-models
```

## By Use Case

- **Blog/CMS** → django-models, django-admin
- **Form-heavy app** → django-forms, django-models
- **API** → django-views, django-models
- **Background tasks** → django-commands
