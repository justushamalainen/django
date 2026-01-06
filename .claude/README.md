# Django Claude Skills

A toolkit for building Django applications with AI assistance.

## Quick Start

1. **Find the right skill**: Check [SKILLS_INDEX.md](SKILLS_INDEX.md)
2. **Read the documentation**: Each skill is in `skills/[skill-name]/SKILL.md`
3. **Check reference patterns**: See `skills/[skill-name]/reference/`

## Available Skills

| Skill | Purpose |
|-------|---------|
| [django-models](skills/django-models/SKILL.md) | Data modeling, ORM queries, migrations |
| [django-forms](skills/django-forms/SKILL.md) | Form creation, validation, widgets |
| [django-views](skills/django-views/SKILL.md) | FBV/CBV patterns, URL configuration |
| [django-admin](skills/django-admin/SKILL.md) | Admin customization, actions, filters |
| [django-templates](skills/django-templates/SKILL.md) | Template tags, filters, inheritance |
| [django-testing](skills/django-testing/SKILL.md) | Unit tests, mocking, fixtures |
| [django-commands](skills/django-commands/SKILL.md) | Management commands |

## Structure

```
.claude/
├── README.md                    # This file
├── SKILLS_INDEX.md              # Find skills by task
└── skills/
    └── [skill-name]/
        ├── SKILL.md             # Main documentation
        └── reference/           # Pattern documentation
```

## Requirements

- Django 5.0+
- Python 3.10+

## Documentation

- [Skills Index](SKILLS_INDEX.md) - Find the right skill for your task
- [Skills Plan](DJANGO_SKILLS_PLAN.md) - Architecture overview
- [Skill Creation Guide](SKILL_CREATION_GUIDE.md) - How to create new skills
