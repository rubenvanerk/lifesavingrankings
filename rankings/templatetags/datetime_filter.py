# -*- coding: utf-8 -*-
"""Application filter for `datetime`_ 24 hours.

.. _datetime: https://docs.python.org/2/library/datetime.html
"""
from datetime import date, timedelta

from django import template

register = template.Library()


@register.filter(name='format_time')
def format_time(value):
    if value is None:
        return ''

    prefix = ''
    if value < timedelta(0):
        prefix = '- '
        value = -value
    hours, rem = divmod(value.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    tens = int(round(value.microseconds / 10000))
    if tens < 10:
        tens = str('0') + str(tens)
    if seconds < 10:
        seconds = str('0') + str(seconds)

    return prefix + '{}:{}.{}'.format(minutes, seconds, tens)


@register.filter
def in_future(value):
    return value > date.today()
