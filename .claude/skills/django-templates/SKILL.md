# Django Templates Skill

## Overview

Master Django's template system for building user interfaces. This skill covers template inheritance, common tags and filters, and context basics.

**When to use this skill:**
- Creating HTML interfaces for Django views
- Building reusable template components
- Working with template inheritance
- Debugging template rendering issues

## Quick Start

Create a base template with inheritance:

```django
{# templates/base.html #}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}My Site{% endblock %}</title>
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
    {% block extra_head %}{% endblock %}
</head>
<body>
    <header>{% include 'partials/header.html' %}</header>
    <main>{% block content %}{% endblock %}</main>
    <footer>{% include 'partials/footer.html' %}</footer>
    {% block extra_js %}{% endblock %}
</body>
</html>

{# templates/page.html #}
{% extends 'base.html' %}

{% block title %}{{ page.title }} - {{ block.super }}{% endblock %}

{% block content %}
    <h1>{{ page.title }}</h1>
    <div>{{ page.content|safe }}</div>
{% endblock %}
```

## Django-Specific Patterns

### Template Inheritance

**Include parent block content:**
```django
{% block title %}Dashboard - {{ block.super }}{% endblock %}
```

**Common block names:**
- `title`, `content`, `extra_head`, `extra_js`

**Include with isolated context:**
```django
{% include "form.html" with form=user_form only %}
```

### Loop Variables

```django
{% for item in items %}
    {{ forloop.counter }}      {# 1-indexed #}
    {{ forloop.counter0 }}     {# 0-indexed #}
    {{ forloop.first }}        {# Boolean #}
    {{ forloop.last }}         {# Boolean #}
{% empty %}
    <li>No items found</li>
{% endfor %}
```

### URL Tag with Namespaces

```django
{% url 'article_detail' article.pk %}          {# Positional #}
{% url 'blog:post_list' %}                     {# Namespace #}
{% url 'edit' pk=article.pk slug=article.slug %} {# Named args #}
```

### Static Files

```django
{% load static %}
<img src="{% static 'images/logo.png' %}">
```

### CSRF Token (Required)

```django
<form method="post">
    {% csrf_token %}  {# Always required for POST #}
    {{ form.as_p }}
</form>
```

### Cache Expensive Operations

```django
{% with total=items.count %}
    {{ total }} item{{ total|pluralize }}
{% endwith %}
```

## Key Filters

### Defaults
```django
{{ value|default:"N/A" }}           {# Falsy values #}
{{ value|default_if_none:"N/A" }}   {# Only None #}
```

### Pluralization
```django
{{ count|pluralize }}               {# 's' for plurals #}
{{ count|pluralize:"y,ies" }}       {# candy/candies #}
```

### Safety
```django
{{ text }}                          {# Auto-escaped #}
{{ html|safe }}                     {# NEVER on user input! #}
```

### Dates
```django
{{ post.created|date:"Y-m-d" }}     {# 2024-03-15 #}
{{ post.created|timesince }}        {# 3 hours ago #}
```

## Best Practices

1. **Keep logic minimal** - Complex logic belongs in views or custom tags
2. **Use template inheritance** - Create a base template and extend it
3. **Never use `|safe` on user input** - Prevents XSS attacks
4. **Always include `{% csrf_token %}`** - Required for POST forms
5. **Use `{% url %}` instead of hardcoded URLs** - Maintainability
6. **Load static files properly** - Always `{% load static %}`
7. **Provide defaults for optional variables** - Use `|default` filter
8. **Keep inheritance shallow** - Avoid more than 2-3 levels

## Reference Documentation

- [Built-in Tags](reference/built_in_tags.md) - Common template tags
- [Built-in Filters](reference/built_in_filters.md) - Common template filters
