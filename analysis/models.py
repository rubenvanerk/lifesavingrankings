from django.db import models
from django.db.models import ForeignKey

from rankings.models import Event, Athlete
from django.contrib.auth.models import User


class SpecialResult(models.Model):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2
    GENDER_CHOICES = (
        (UNKNOWN, 'Unknown'),
        (MALE, 'Male'),
        (FEMALE, 'Female')
    )

    gender = models.IntegerField(default=UNKNOWN, choices=GENDER_CHOICES)

    event = ForeignKey(Event)
    time = models.DurationField()

    def __str__(self):
        return self.time


class AnalysisGroup(models.Model):
    name = models.CharField(max_length=60)
    creator = ForeignKey(User)
    public = models.BooleanField(default=False)
    athlete = models.ManyToManyField(Athlete)
