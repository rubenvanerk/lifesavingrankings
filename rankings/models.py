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
        return athlete[0]


class Event(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name

    @classmethod
    def find_by_name(cls, event_name):
        event = Event.objects.raw(
            "SELECT * FROM rankings_event " 
            "WHERE LOWER(REPLACE(name, ' ', '')) = %s "
            "LIMIT 1",
            [event_name]
        )
        return event[0]


class Competition(models.Model):
    name = models.CharField(max_length=60, unique=True)
    date = models.DateField()
    location = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class IndividualResult(models.Model):
    athlete = ForeignKey(Athlete, on_delete=models.CASCADE)
    event = ForeignKey(Event, on_delete=models.CASCADE)
    competition = ForeignKey(Competition,on_delete=models.CASCADE)
    time = models.DurationField()

    @staticmethod
    def find_by_athlete(athlete):
        return IndividualResult.objects.filter(athlete=athlete)

    @staticmethod
    def find_by_athlete_and_event(athlete, event):
        return IndividualResult.objects.filter(athlete=athlete, event=event)