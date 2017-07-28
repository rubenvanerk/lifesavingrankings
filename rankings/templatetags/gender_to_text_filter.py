# -*- coding: utf-8 -*-

from django import template

register = template.Library()


@register.filter(name='gender_to_text')
def gender_to_text(gender):
    if gender == 1:
        gender = 'men'
    elif gender == 2:
        gender = 'women'
    else:
        gender = 0

    return gender
