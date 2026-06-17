# Django Built-in Template Filters Reference

Quick reference for Django-specific filter behaviors.

## Safety Filters (Critical)

### safe
**NEVER use on user input!**
```django
{{ trusted_html|safe }}  {# Only for trusted sources #}
```

### Auto-escaping behavior
```django
{{ text }}  {# Auto-escaped by default #}
```

## Date Filters

**Format strings:**
```django
{{ value|date:"Y-m-d" }}        {# 2024-03-15 #}
{{ value|date:"F j, Y" }}       {# March 15, 2024 #}
{{ value|date:"l, F j, Y" }}    {# Friday, March 15, 2024 #}
{{ value|time:"H:i" }}          {# 14:30 #}
{{ value|time:"g:i A" }}        {# 2:30 PM #}
```

**Relative dates:**
```django
{{ blog_date|timesince }}       {# 3 days, 4 hours #}
{{ event_date|timeuntil }}      {# 5 days, 2 hours #}
```

## Logic Filters

### default vs default_if_none

**Important distinction:**
```django
{{ value|default:"N/A" }}           {# Falsy: False, "", None, 0, [] #}
{{ value|default_if_none:"N/A" }}   {# Only None (0 and False pass through) #}
```

### yesno

```django
{{ value|yesno:"Yes,No,Maybe" }}    {# True → Yes, False → No, None → Maybe #}
```

## Django-Specific Filters

### pluralize

**Custom plural forms:**
```django
{{ count|pluralize }}               {# "s" for plurals #}
{{ count|pluralize:"y,ies" }}       {# candy/candies #}
{{ count|pluralize:"es" }}          {# box/boxes #}
```

### filesizeformat

```django
{{ 123456789|filesizeformat }}      {# 117.7 MB #}
```

### json_script

**Safe JSON injection:**
```django
{{ data|json_script:"my-data" }}
<script>
    const data = JSON.parse(document.getElementById('my-data').textContent);
</script>
```

### slugify

```django
{{ "Joel is a slug"|slugify }}      {# joel-is-a-slug #}
```
