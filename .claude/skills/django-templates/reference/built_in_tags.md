# Django Built-in Template Tags Reference

Essential Django template tags for common tasks.

## Control Flow Tags

### if

Test a condition and render content conditionally.

```django
{% if condition %}
    Content
{% endif %}
```

**With elif and else:**
```django
{% if user.is_superuser %}
    <p>Admin access</p>
{% elif user.is_staff %}
    <p>Staff access</p>
{% else %}
    <p>Regular user</p>
{% endif %}
```

**Operators:**
- `==`, `!=` - Equality
- `<`, `>`, `<=`, `>=` - Comparison
- `in`, `not in` - Contains
- `and`, `or`, `not` - Boolean operators

**Example:**
```django
{% if user.is_active and user.is_verified %}
    <p>Welcome!</p>
{% endif %}
```

### for

Iterate over a sequence.

```django
{% for item in item_list %}
    <li>{{ item }}</li>
{% endfor %}
```

**With empty clause:**
```django
{% for item in item_list %}
    <li>{{ item }}</li>
{% empty %}
    <li>No items available.</li>
{% endfor %}
```

**Loop variables:**
```django
{% for item in items %}
    {{ forloop.counter }}      {# 1-indexed #}
    {{ forloop.counter0 }}     {# 0-indexed #}
    {{ forloop.first }}        {# True on first iteration #}
    {{ forloop.last }}         {# True on last iteration #}
{% endfor %}
```

**Unpacking:**
```django
{% for key, value in dictionary.items %}
    {{ key }}: {{ value }}
{% endfor %}
```

## Template Structure Tags

### extends

Declare template inheritance.

```django
{% extends "base.html" %}
```

**Dynamic parent:**
```django
{% extends parent_template %}  {# Variable from context #}
```

**Must be first tag** (except for comments and `{% load %}`):
```django
{% load static %}
{% extends "base.html" %}
```

### block

Define overridable content sections.

```django
{# In parent template #}
{% block content %}
    Default content
{% endblock %}

{# In child template #}
{% block content %}
    Overridden content
{% endblock %}
```

**Include parent content:**
```django
{% block content %}
    {{ block.super }}
    Additional content
{% endblock %}
```

### include

Include another template.

```django
{% include "sidebar.html" %}
```

**With context variables:**
```django
{% include "name_snippet.html" with person="Jane" greeting="Hello" %}
```

**Isolated context (only specified variables):**
```django
{% include "name_snippet.html" with person="Jane" only %}
```

### load

Load custom template tag library.

```django
{% load static %}
{% load i18n %}
{% load custom_tags %}
```

**Multiple libraries:**
```django
{% load static i18n %}
```

## URL and Static Tags

### url

Generate URLs from view names.

```django
{% url 'view_name' %}
{% url 'namespace:view_name' %}
```

**With arguments:**
```django
{% url 'article_detail' article.pk %}
{% url 'article_detail' pk=article.pk slug=article.slug %}
```

**Assign to variable:**
```django
{% url 'article_detail' article.pk as article_url %}
<a href="{{ article_url }}">Read more</a>
```

### static

Generate URLs for static files.

```django
{% load static %}
<img src="{% static 'images/logo.png' %}" alt="Logo">
<link rel="stylesheet" href="{% static 'css/style.css' %}">
<script src="{% static 'js/app.js' %}"></script>
```

**Assign to variable:**
```django
{% static 'images/hero.jpg' as hero_image %}
<div style="background-image: url({{ hero_image }})"></div>
```

## Data Manipulation Tags

### with

Assign values to variables in a scope.

```django
{% with total=business.employees.count %}
    {{ total }} employee{{ total|pluralize }}
{% endwith %}
```

**Multiple variables:**
```django
{% with alpha=1 beta=2 %}
    Sum: {{ alpha|add:beta }}
{% endwith %}
```

**Cache expensive operations:**
```django
{% with entries=blog.entries.all %}
    {% for entry in entries %}
        {{ entry.title }}
    {% endfor %}
    Total: {{ entries|length }}
{% endwith %}
```

### csrf_token

Include CSRF token for forms.

```django
<form method="post">
    {% csrf_token %}
    ...
</form>
```

**Required for all POST forms** to prevent Cross-Site Request Forgery attacks.

## Other Useful Tags

### comment

Multi-line comments.

```django
{% comment %}
    This is a comment.
    It can span multiple lines.
{% endcomment %}
```

### now

Output current date/time.

```django
{% now "Y-m-d" %}
{% now "D d M Y" %}
{% now "Y" as current_year %}
```

### cycle

Cycle through values in a loop.

```django
{% for item in items %}
    <tr class="{% cycle 'row1' 'row2' %}">
        <td>{{ item }}</td>
    </tr>
{% endfor %}
```

## Common Patterns

### Conditional CSS classes
```django
<div class="{% if user.is_premium %}premium{% else %}standard{% endif %}">
```

### Alternating row colors
```django
{% for item in items %}
    <tr class="{% cycle 'odd' 'even' %}">
        <td>{{ item }}</td>
    </tr>
{% endfor %}
```

### Breadcrumbs
```django
{% for crumb in breadcrumbs %}
    <a href="{% url crumb.view %}">{{ crumb.title }}</a>
    {% if not forloop.last %} › {% endif %}
{% endfor %}
```

### Active navigation
```django
<nav>
    <a href="{% url 'home' %}" class="{% if request.resolver_match.url_name == 'home' %}active{% endif %}">
        Home
    </a>
</nav>
```
