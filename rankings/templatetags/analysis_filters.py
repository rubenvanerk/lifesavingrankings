# -*- coding: utf-8 -*-

from django import template
from .datetime_filter import format_datetime

register = template.Library()


@register.filter(name='find_special_time_by_event')
def find_special_time_by_event(special_results, event):
    for result in special_results:
        if result.event == event:
            return format_datetime(result.time)
    return 0


@register.filter(name='calculate_percentage')
def calculate_percentage(result, special_results):
    for special_result in special_results:
        if result.event.pk == special_result.event.id:
            personal_best = result.time.seconds + (result.time.microseconds / 1000000)
            special_result_time = special_result.time.seconds + (special_result.time.microseconds / 1000000)
            percentage = round(personal_best / special_result_time * 100, 1)
            return str(percentage) + '%'
    return ""
