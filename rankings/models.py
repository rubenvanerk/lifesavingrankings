from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.db.models import ForeignKey, Q, Max
from django.urls import reverse
from django.utils.text import slugify
from rankings.functions import calculate_points


class Nationality(models.Model):
    name = models.CharField(max_length=100, unique=True, null=True)
    flag_code = models.CharField(max_length=10, null=True)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.SET_NULL)
    is_parent_country = models.BooleanField(default=False)
    lenex_code = models.CharField(max_length=3, unique=True, null=True)

    def __str__(self):
        return self.name

    def get_children_pks(self):
        nationality_pks = [self.pk]
        for child in self.children.all():
            nationality_pks += child.get_children_pks()
        return nationality_pks


class Athlete(models.Model):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2
    GENDER_CHOICES = (
        (UNKNOWN, 'Unknown'),
        (MALE, 'Male'),
        (FEMALE, 'Female')
    )

    first_name = models.CharField(max_length=20, null=True, default=None, blank=True)
    last_name = models.CharField(max_length=30, null=True, default=None, blank=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True)

    year_of_birth = models.IntegerField(null=True, blank=True)
    gender = models.IntegerField(default=UNKNOWN, choices=GENDER_CHOICES)
    nationalities = models.ManyToManyField(Nationality, related_name='nationalities', default=None, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('athlete-overview', args=[self.slug])

    def get_total_points(self):
        events = Event.objects.filter(use_points_in_athlete_total=True)
        total_points = 0
        for event in events:
            result = IndividualResult.objects.filter(event=event, athlete=self).aggregate(Max('points'))
            if result['points__max'] is not None:
                total_points += result['points__max']
        return round(total_points, 2)

    def get_personal_bests(self):
        events = Event.objects.filter(use_points_in_athlete_total=True)
        personal_bests = []
        for event in events:
            personal_best = IndividualResult.objects.filter(event=event, athlete=self).order_by('time').first()
            if personal_best:
                personal_bests.append(personal_best)
        return personal_bests

    def get_competitions(self):
        results = IndividualResult.objects.filter(athlete=self).values('competition')
        competitions = Competition.objects.filter(pk__in=results).order_by('date')
        return competitions

    def count_results(self):
        return IndividualResult.objects.filter(athlete=self).count()

    def count_competitions(self):
        return IndividualResult.objects.filter(athlete=self).values_list('competition', flat=True).distinct().count()


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
    use_points_in_athlete_total = models.BooleanField(default=False)

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
        if type(gender) is not int:
            if gender is 'men':
                gender = 1
            else:
                gender = 2
        query_set = IndividualResult.objects.filter(event=self, athlete__gender=gender)
        if competition is not None:
            max_round = IndividualResult.objects.filter(event=self, athlete__gender=gender, competition=competition).aggregate(Max('round'))['round__max']
            query_set = query_set.filter(competition=competition, round=max_round)
        else:
            query_set = query_set.filter(disqualified=False)

        return query_set.order_by('time')[:limit]


class Competition(models.Model):
    class Meta:
        ordering = ['-published_on']
    UNKNOWN = 0
    ELECTRONIC = 1
    BY_HAND = 2
    TYPES = (
        (UNKNOWN, 'Unknown'),
        (ELECTRONIC, 'Electronic'),
        (BY_HAND, 'By hand')
    )
    SCHEDULED = 1
    IMPORTED = 2
    UNABLE_TO_IMPORT = 3
    WANTED = 4
    STATUS_OPTIONS = (
        (SCHEDULED, 'Scheduled for import'),
        (IMPORTED, 'Imported'),
        (UNABLE_TO_IMPORT, 'Unable to import'),
        (WANTED, 'Wanted')
    )
    name = models.CharField(max_length=100, unique=True, null=True)
    slug = models.SlugField(null=True)
    date = models.DateField()
    location = models.CharField(max_length=100)
    type_of_timekeeping = models.IntegerField(default=ELECTRONIC, choices=TYPES)
    is_concept = models.BooleanField(default=False)
    published_on = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(default=IMPORTED, choices=STATUS_OPTIONS)
    file_name = models.CharField(max_length=100, null=True, blank=True)
    credit = models.CharField(max_length=512, null=True, blank=True)

    prepopulated_fields = {"slug": ("name",)}

    def __str__(self):
        if self.name:
            return self.name
        return 'unknown ' + str(self.pk)

    def get_athlete_count(self):
        return IndividualResult.objects.filter(competition=self).values('athlete').distinct().count()

    def get_result_count(self):
        return IndividualResult.objects.filter(competition=self).count()

    def get_absolute_url(self):
        return reverse('competition-overview', args=[self.slug])

    def get_athletes(self):
        return Athlete.objects.filter(
            pk__in=IndividualResult.objects.filter(competition=self).values('athlete').distinct())

    def is_fully_labeled(self):
        return Athlete.objects.filter(nationalities=None,
                                      pk__in=IndividualResult.objects.filter(competition=self).values(
                                          'athlete').distinct()).count() < 1

    def is_imported(self):
        return self.status == self.IMPORTED

    def get_unlabeled_athletes(self):
        athlete_ids = IndividualResult.objects.filter(competition=self).values('athlete').distinct()
        return Athlete.objects.filter(pk__in=athlete_ids, nationalities=None).all()


class IndividualResult(models.Model):
    athlete = ForeignKey(Athlete, on_delete=models.CASCADE)
    event = ForeignKey(Event, on_delete=models.CASCADE)
    competition = ForeignKey(Competition, on_delete=models.CASCADE)
    time = models.DurationField()
    points = models.FloatField(default=0)
    original_line = models.CharField(max_length=200, null=True, default=None)
    round = models.IntegerField(default=0)
    disqualified = models.BooleanField(default=False)
    did_not_start = models.BooleanField(default=False)

    extra_analysis_time_by = ForeignKey(User, on_delete=models.CASCADE, null=True, default=None, blank=True)

    class Meta:
        ordering = ['time']

    def __str__(self):
        return self.athlete.name + ' ' + self.event.name + ' ' + str(self.time)

    def calculate_points(self):
        record = EventRecord.objects.filter(gender=self.athlete.gender, event=self.event).first()
        if self.disqualified or not record:
            return
        self.points = calculate_points(record.time.total_seconds() * 100, self.time.total_seconds() * 100)
        self.save()

    def get_time_display(self):
        if self.disqualified:
            return 'DQ'
        if self.did_not_start:
            return 'DNS'
        hours, rem = divmod(self.time.seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        tens = int(round(self.time.microseconds / 10000))
        if tens < 10:
            tens = str('0') + str(tens)
        if seconds < 10:
            seconds = str('0') + str(seconds)

        return '{}:{}.{}'.format(minutes, seconds, tens)

    @staticmethod
    def find_by_athlete(athlete):
        return IndividualResult.objects.filter(athlete=athlete)

    @staticmethod
    def find_by_athlete_and_event(athlete, event):
        return IndividualResult.objects.filter(athlete=athlete, event=event)

    @staticmethod
    def find_fastest_by_athlete_and_event(athlete, event, analysis_group):
        qs = IndividualResult.objects.filter(athlete=athlete, event=event).order_by('time')
        qs = qs.filter(Q(extra_analysis_time_by=analysis_group.creator) | Q(extra_analysis_time_by=None))
        return qs.first()


class EventRecord(models.Model):
    def __str__(self):
        return self.event.name + " " + self.get_gender_display()

    UNKNOWN = 0
    MALE = 1
    FEMALE = 2
    GENDER_CHOICES = (
        (UNKNOWN, 'Unknown'),
        (MALE, 'Male'),
        (FEMALE, 'Female')
    )

    gender = models.IntegerField(default=UNKNOWN, choices=GENDER_CHOICES)
    event = ForeignKey(Event, on_delete=models.CASCADE)
    time = models.DurationField()


class RelayOrder(models.Model):
    event = ForeignKey(Event, on_delete=models.CASCADE, related_name='relay')
    segment = ForeignKey(Event, on_delete=models.CASCADE, related_name='segment')
    index = models.IntegerField()


class MergeRequest(models.Model):
    athletes = models.ManyToManyField(Athlete)
