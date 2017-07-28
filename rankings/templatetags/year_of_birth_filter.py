# -*- coding: utf-8 -*-

from django import template

register = template.Library()


@register.filter(name='format_year_of_birth')
def format_datetime(value):
    if value < 10:
        return str(0) + str(value)
    return value
