# -*- coding: utf-8 -*-

from django import template
from rankings.models import Athlete

register = template.Library()


@register.filter(name='id_to_athlete_name')
def id_to_athlete_name(athlete_id):
    athlete = Athlete.objects.filter(id=athlete_id).first()
    return athlete.name
