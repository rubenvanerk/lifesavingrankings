# -*- coding: utf-8 -*-

from django import template

register = template.Library()


@register.filter(name='to_url')
def to_url(url):
    url = url.replace(" ", "-")
    url = url.lower()

    return url
