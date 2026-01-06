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

## Template Inheritance

### extends and block

Use `{% extends %}` to inherit from a parent template:

```django
{% extends "base.html" %}

{% block content %}
    <h1>My Page</h1>
{% endblock %}
```

**Include parent content with `{{ block.super }}`:**
```django
{% block title %}Dashboard - {{ block.super }}{% endblock %}
```

**Common block names:**
- `title` - Page title
- `content` - Main content area
- `extra_head` - Additional CSS/meta tags
- `extra_js` - Additional JavaScript

### include

Include reusable template fragments:

```django
{% include "partials/nav.html" %}
{% include "components/card.html" with title="Profile" %}
{% include "components/form.html" with form=user_form only %}
```

## Common Tags

### Control Flow

**if/elif/else:**
```django
{% if user.is_authenticated %}
    <p>Welcome, {{ user.username }}!</p>
{% elif user.is_staff %}
    <p>Staff access</p>
{% else %}
    <p>Please log in</p>
{% endif %}
```

**for loops:**
```django
{% for item in items %}
    <li>{{ forloop.counter }}. {{ item.name }}</li>
{% empty %}
    <li>No items found</li>
{% endfor %}
```

**Loop variables:**
- `{{ forloop.counter }}` - 1-indexed iteration count
- `{{ forloop.first }}` - True on first iteration
- `{{ forloop.last }}` - True on last iteration

### URLs and Static Files

**Generate URLs:**
```django
<a href="{% url 'article_detail' article.pk %}">Read more</a>
<a href="{% url 'blog:post_list' %}">Blog</a>
```

**Static files:**
```django
{% load static %}
<img src="{% static 'images/logo.png' %}" alt="Logo">
<link rel="stylesheet" href="{% static 'css/style.css' %}">
```

### Forms

**Always include CSRF token in POST forms:**
```django
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Submit</button>
</form>
```

### Variable Caching

Use `{% with %}` to cache expensive operations:

```django
{% with total=items.count %}
    <p>{{ total }} item{{ total|pluralize }}</p>
{% endwith %}
```

## Common Filters

### String Manipulation
```django
{{ text|lower }}                    {# Lowercase #}
{{ text|upper }}                    {# Uppercase #}
{{ text|title }}                    {# Title Case #}
{{ text|truncatewords:30 }}         {# Truncate to 30 words #}
{{ text|truncatechars:100 }}        {# Truncate to 100 chars #}
```

### Dates
```django
{{ post.created|date:"Y-m-d" }}     {# 2024-03-15 #}
{{ post.created|date:"F j, Y" }}    {# March 15, 2024 #}
{{ post.created|timesince }}        {# 3 hours ago #}
```

### Lists
```django
{{ items|length }}                  {# Count #}
{{ items|first }}                   {# First item #}
{{ items|last }}                    {# Last item #}
{{ items|join:", " }}               {# Join with comma #}
```

### Defaults and Logic
```django
{{ value|default:"N/A" }}           {# Default if falsy #}
{{ value|default_if_none:"N/A" }}   {# Default if None #}
{{ count|pluralize }}               {# 's' for plurals #}
{{ count|pluralize:"y,ies" }}       {# candy/candies #}
```

### Safety
```django
{{ text }}                          {# Auto-escaped (safe) #}
{{ html|safe }}                     {# Mark as safe - trusted only! #}
{{ text|escape }}                   {# Force escape #}
{{ text|striptags }}                {# Remove HTML tags #}
```

## Context Basics

Templates receive context from views:

```python
# views.py
def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    return render(request, 'article_detail.html', {
        'article': article,
        'related': article.related_articles.all()[:5],
    })
```

Access in template:
```django
<h1>{{ article.title }}</h1>
<p>By {{ article.author.name }}</p>
<p>{{ article.content|safe }}</p>

<h2>Related Articles</h2>
{% for item in related %}
    <a href="{% url 'article_detail' item.pk %}">{{ item.title }}</a>
{% endfor %}
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
