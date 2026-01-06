# Django Built-in Template Filters Reference

Essential Django template filters for common tasks.

## String Filters

### lower
Convert string to lowercase.
```django
{{ "HELLO WORLD"|lower }}
{# Output: hello world #}
```

### upper
Convert string to uppercase.
```django
{{ "hello world"|upper }}
{# Output: HELLO WORLD #}
```

### title
Convert to title case.
```django
{{ "hello world"|title }}
{# Output: Hello World #}
```

### capfirst
Capitalize the first character.
```django
{{ "hello world"|capfirst }}
{# Output: Hello world #}
```

### truncatewords
Truncate after specified number of words.
```django
{{ "This is a long sentence with many words"|truncatewords:5 }}
{# Output: This is a long sentence ... #}
```

### truncatechars
Truncate after specified number of characters.
```django
{{ "This is a long string"|truncatechars:13 }}
{# Output: This is a ... #}
```

### slugify
Convert to URL-friendly slug.
```django
{{ "Joel is a slug"|slugify }}
{# Output: joel-is-a-slug #}
```

## HTML and Safety Filters

### safe
Mark string as safe (no escaping).
```django
{{ "<strong>Bold</strong>"|safe }}
{# Output: <strong>Bold</strong> #}
```

**Warning:** Never use on untrusted user input!

### escape
Escape HTML characters.
```django
{{ "<script>alert('XSS')</script>"|escape }}
{# Output: &lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt; #}
```

### linebreaks
Convert newlines to `<p>` and `<br>` tags.
```django
{{ "Line 1\nLine 2\n\nLine 3"|linebreaks }}
{# Output: <p>Line 1<br>Line 2</p><p>Line 3</p> #}
```

### linebreaksbr
Convert newlines to `<br>` tags.
```django
{{ "Line 1\nLine 2"|linebreaksbr }}
{# Output: Line 1<br>Line 2 #}
```

### striptags
Remove all HTML tags.
```django
{{ "<p>Hello <strong>world</strong>!</p>"|striptags }}
{# Output: Hello world! #}
```

## List and Sequence Filters

### first
Return first item in list.
```django
{{ [1, 2, 3]|first }}
{# Output: 1 #}
```

### last
Return last item in list.
```django
{{ [1, 2, 3]|last }}
{# Output: 3 #}
```

### join
Join list with string.
```django
{{ ['apple', 'banana', 'cherry']|join:", " }}
{# Output: apple, banana, cherry #}
```

### length
Return length of value.
```django
{{ [1, 2, 3]|length }}
{# Output: 3 #}

{{ "Django"|length }}
{# Output: 6 #}
```

### slice
Return slice of sequence.
```django
{{ "Django"|slice:":2" }}
{# Output: Dj #}

{{ items|slice:":3" }}
{# First 3 items #}
```

## Number Filters

### add
Add argument to value.
```django
{{ 4|add:2 }}
{# Output: 6 #}

{{ "hello "|add:"world" }}
{# Output: hello world #}
```

### floatformat
Format float to specified decimal places.
```django
{{ 34.23234|floatformat }}
{# Output: 34.2 (default 1 decimal) #}

{{ 34.23234|floatformat:3 }}
{# Output: 34.232 #}
```

## Date and Time Filters

### date
Format date.
```django
{{ value|date:"Y-m-d" }}
{# Output: 2024-03-15 #}

{{ value|date:"F j, Y" }}
{# Output: March 15, 2024 #}
```

**Common format strings:**
```django
"Y-m-d"               {# 2024-03-15 #}
"d/m/Y"               {# 15/03/2024 #}
"F j, Y"              {# March 15, 2024 #}
"l, F j, Y"           {# Friday, March 15, 2024 #}
```

### time
Format time.
```django
{{ value|time:"H:i" }}
{# Output: 14:30 #}

{{ value|time:"g:i A" }}
{# Output: 2:30 PM #}
```

### timesince
Format as time since given date.
```django
{{ blog_date|timesince }}
{# Output: 3 days, 4 hours #}
```

### timeuntil
Format as time until given date.
```django
{{ event_date|timeuntil }}
{# Output: 5 days, 2 hours #}
```

## Logic Filters

### default
Provide default value if variable is falsy.
```django
{{ value|default:"nothing" }}
{# If value is False, "", None, 0, empty list, returns "nothing" #}

{{ items|default:"No items available" }}
```

### default_if_none
Provide default only if variable is None.
```django
{{ value|default_if_none:"N/A" }}
{# Only returns "N/A" if value is None (not False or 0) #}
```

### yesno
Map True/False/None to custom strings.
```django
{{ value|yesno:"Yes,No,Maybe" }}
{# True → Yes, False → No, None → Maybe #}

{{ user.is_active|yesno:"Active,Inactive" }}
```

## URL Filters

### urlencode
URL-encode value.
```django
{{ "hello world"|urlencode }}
{# Output: hello%20world #}
```

**Common use:**
```django
<a href="{% url 'search' %}?q={{ query|urlencode }}">Search</a>
```

### urlize
Convert URLs in text to clickable links.
```django
{{ "Visit https://djangoproject.com"|urlize }}
{# Output: Visit <a href="https://djangoproject.com">https://djangoproject.com</a> #}
```

## Utility Filters

### pluralize
Return plural suffix.
```django
You have {{ num_items }} item{{ num_items|pluralize }}
{# 1 item, 2 items, 0 items #}

{{ num_items }} cand{{ num_items|pluralize:"y,ies" }}
{# 1 candy, 2 candies #}
```

### filesizeformat
Format number as file size.
```django
{{ 123456789|filesizeformat }}
{# Output: 117.7 MB #}
```

### json_script
Output value as JSON in script tag.
```django
{{ data|json_script:"user-data" }}
{# Output: <script id="user-data" type="application/json">{"key": "value"}</script> #}
```

**Usage with JavaScript:**
```django
{{ data|json_script:"my-data" }}
<script>
    const data = JSON.parse(document.getElementById('my-data').textContent);
</script>
```

## Chaining Filters

Filters can be chained together:

```django
{{ text|lower|truncatewords:10 }}
{{ user.bio|striptags|truncatechars:100 }}
{{ value|default:"N/A"|upper }}
```

**Order matters:**
```django
{{ "HELLO"|lower|capfirst }}
{# Output: Hello #}

{{ "HELLO"|capfirst|lower }}
{# Output: hello #}
```

## Common Patterns

### Display count with proper pluralization
```django
{{ item_count }} item{{ item_count|pluralize }} found
```

### Format currency
```django
${{ price|floatformat:2 }}
```

### Safe HTML with fallback
```django
{{ content|striptags|truncatewords:50|default:"No content available" }}
```

### User-friendly dates
```django
Posted {{ post.created|timesince }} ago
{# or #}
Posted on {{ post.created|date:"F j, Y" }}
```

### Format lists for display
```django
Tags: {{ post.tags.all|join:", " }}
```

## Best Practices

### 1. Use appropriate escaping
```django
{# BAD - XSS vulnerability #}
{{ user_input|safe }}

{# GOOD #}
{{ user_input }}  {# Auto-escaped #}
{{ trusted_html|safe }}  {# Only for trusted sources #}
```

### 2. Provide user-friendly defaults
```django
{{ profile.bio|default:"No bio provided" }}
{{ post.published_date|date:"F j, Y"|default:"Not published" }}
```

### 3. Handle empty lists gracefully
```django
{% if items %}
    {{ items|join:", " }}
{% else %}
    No items available
{% endif %}
```
