# Django Built-in Template Tags Reference

Quick reference for Django-specific tag behaviors.

## Control Flow

### for

**Django-specific `{% empty %}` clause:**
```django
{% for item in items %}
    {{ item }}
{% empty %}
    No items available.
{% endfor %}
```

**Loop variables:**
```django
{{ forloop.counter }}      {# 1-indexed (Django-specific) #}
{{ forloop.counter0 }}     {# 0-indexed #}
{{ forloop.first }}        {# Boolean #}
{{ forloop.last }}         {# Boolean #}
{{ forloop.parentloop }}   {# Access outer loop #}
```

## Template Structure

### extends

**Must be first tag** (except `{% load %}` and comments):
```django
{% load static %}
{% extends "base.html" %}
```

**Dynamic parent:**
```django
{% extends parent_template %}
```

### block

**Include parent content:**
```django
{% block content %}
    {{ block.super }}  {# Django-specific #}
{% endblock %}
```

### include

**Isolated context (Django-specific):**
```django
{% include "form.html" with form=user_form only %}
```

## URL Tags

### url

**With namespaces:**
```django
{% url 'namespace:view_name' %}
{% url 'article_detail' article.pk %}
{% url 'article_detail' pk=article.pk slug=article.slug %}
```

**As variable:**
```django
{% url 'article_detail' article.pk as article_url %}
```

### static

**Requires `{% load static %}`:**
```django
{% load static %}
<img src="{% static 'images/logo.png' %}">
```

## Other Tags

### with

**Cache expensive operations:**
```django
{% with total=items.count %}
    {{ total }} item{{ total|pluralize }}
{% endwith %}
```

### csrf_token

**Required for all POST forms:**
```django
<form method="post">
    {% csrf_token %}
</form>
```

### now

```django
{% now "Y-m-d" %}
{% now "Y" as current_year %}
```

### cycle

**Alternate values in loops:**
```django
{% for item in items %}
    <tr class="{% cycle 'row1' 'row2' %}">
        <td>{{ item }}</td>
    </tr>
{% endfor %}
```
