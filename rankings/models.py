from __future__ import unicode_literals

from django.db import models
from django.db.models import ForeignKey


class Athlete(models.Model):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2
    GENDER_CHOICES = (
        (UNKNOWN, 'Unknown'),
        (MALE, 'Male'),
        (FEMALE, 'Female')
    )

    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=30)
    slug = models.URLField(unique=True, null=True)

    year_of_birth = models.IntegerField()
    gender = models.IntegerField(default=UNKNOWN, choices=GENDER_CHOICES)

    def __str__(self):
        name_str = self.first_name + " " + self.last_name
        return name_str

    def to_url(self):
        url = self.first_name + self.last_name
        url = url.replace(" ", "")
        url = url.lower()
        return url

    @staticmethod
    def find_by_name(name):
        athlete = Athlete.objects.raw(
            "SELECT * FROM rankings_athlete "
            "WHERE POSITION(LOWER(REPLACE(first_name, ' ', '')) in %s) != 0 "
            "AND POSITION(LOWER(REPLACE(last_name, ' ', '')) in %s) != 0 "
            "LIMIT 1",
            [name, name]
        )
        for result in athlete:
            return result
        return False


class Event(models.Model):
    UNKNOWN = 0
    INDIVIDUAL = 1
    RELAY_SEGMENT = 2
    TYPES = (
        (UNKNOWN, 'Unknown'),
        (INDIVIDUAL, 'Individual'),
        (RELAY_SEGMENT, 'Relay segment')
    )
    name = models.CharField(max_length=60)
    type = models.IntegerField(default=UNKNOWN, choices=TYPES)

    def __str__(self):
        return self.name

    @classmethod
    def find_by_name(cls, event_name):
        event = Event.objects.raw(
            "SELECT * FROM rankings_event " 
            "WHERE LOWER(REPLACE(name, ' ', '-')) = %s "
            "LIMIT 1",
            [event_name]
        )
        if len(list(event)):
            return event[0]
        else:
            return False


class Competition(models.Model):
    UNKNOWN = 0
    ELECTRONIC = 1
    BY_HAND = 2
    TYPES = (
        (UNKNOWN, 'Unknown'),
        (ELECTRONIC, 'Electronic'),
        (BY_HAND, 'By hand')
    )
    name = models.CharField(max_length=60, unique=True)
    date = models.DateField()
    location = models.CharField(max_length=30)
    type_of_timekeeping = models.IntegerField(default=ELECTRONIC, choices=TYPES)

    def __str__(self):
        return self.name


class IndividualResult(models.Model):
    athlete = ForeignKey(Athlete, on_delete=models.CASCADE)
    event = ForeignKey(Event, on_delete=models.CASCADE)
    competition = ForeignKey(Competition, on_delete=models.CASCADE)
    time = models.DurationField()

    @staticmethod
    def find_by_athlete(athlete):
        return IndividualResult.objects.filter(athlete=athlete)

    @staticmethod
    def find_by_athlete_and_event(athlete, event):
        return IndividualResult.objects.filter(athlete=athlete, event=event)
