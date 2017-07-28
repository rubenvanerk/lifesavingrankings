# -*- coding: utf-8 -*-
"""Application filter for `datetime`_ 24 hours.

.. _datetime: https://docs.python.org/2/library/datetime.html
"""

from django import template

register = template.Library()


@register.filter(name='format_time')
def format_datetime(value):
    hours, rem = divmod(value.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    tens = int(round(value.microseconds / 10000))
    if tens < 10:
        tens = str('0') + str(tens)
    if seconds < 10:
        seconds = str('0') + str(seconds)

    return '{}:{}.{}'.format(minutes, seconds, tens)
