from __future__ import unicode_literals

from django.db import models
from django.db.models import ForeignKey
from django.urls import reverse
from django.utils.text import slugify


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
    slug = models.SlugField(unique=True, null=True)
    prepopulated_fields = {"slug": ("first_name", "last_name")}

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

    def get_absolute_url(self):
        return reverse('athlete-overview', args=[self.slug])


class Event(models.Model):
    UNKNOWN = 0
    INDIVIDUAL = 1
    RELAY_SEGMENT = 2
    RELAY_COMPLETE = 3
    TYPES = (
        (UNKNOWN, 'Unknown'),
        (INDIVIDUAL, 'Individual'),
        (RELAY_SEGMENT, 'Relay segment'),
        (RELAY_COMPLETE, 'Relay complete')
    )
    name = models.CharField(max_length=60)
    type = models.IntegerField(default=UNKNOWN, choices=TYPES)

    def __str__(self):
        return self.name

    def generate_slug(self):
        return slugify(self.name)

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

    def are_segments_same(self):
        relay_orders = RelayOrder.objects.filter(event=self).all()
        previous_segment = relay_orders.first().segment
        for relay_order in relay_orders:
            if relay_order.segment.pk is not previous_segment.pk:
                return False
            previous_segment = relay_order.segment
        return True

    def get_top_by_competition_and_gender(self, competition, gender, limit):
        return IndividualResult.objects.filter(event=self, competition=competition, athlete__gender=gender).order_by('time').all()[:limit]


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
    slug = models.SlugField(null=True)
    date = models.DateField()
    location = models.CharField(max_length=30)
    type_of_timekeeping = models.IntegerField(default=ELECTRONIC, choices=TYPES)

    prepopulated_fields = {"slug": ("name",)}

    def __str__(self):
        return self.name

    def get_athlete_count(self):
        return IndividualResult.objects.filter(competition=self).values('athlete').distinct().count()


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

    @staticmethod
    def find_fastest_by_athlete_and_event(athlete, event):
        return IndividualResult.objects.filter(athlete=athlete, event=event).order_by('time').first()


class RelayOrder(models.Model):
    event = ForeignKey(Event, on_delete=models.CASCADE, related_name='relay')
    segment = ForeignKey(Event, on_delete=models.CASCADE, related_name='segment')
    index = models.IntegerField()
