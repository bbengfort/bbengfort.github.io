---
layout: page
title: Archive
icon: archive
---

Welcome to the Archive.

{% for category in site.categories %}

## {{ category | first | capitalize}}

{% for posts in category %}
    {% for post in posts %}
        {% if post.url %}
* [{{ post.title }}]({{ post.url }}) &middot; <time>{{ post.date | date: "%b %-d, %Y" }}</time>
        {% endif %}
    {% endfor %}
{% endfor %}

{% endfor %}
