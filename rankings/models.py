from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector, SearchQuery, TrigramSimilarity, SearchRank
from django.db import models
from django.db.models import ForeignKey, Q, Max, Prefetch, Min, OuterRef, F, Subquery
from django.urls import reverse
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

    # adapted from:
    # https://medium.com/@tnesztler/recursive-queries-as-querysets-for-parent-child-relationships-self-manytomany-in-django-671696dfe47
    def get_all_children(self, include_self=True):
        table_name = Nationality.objects.model._meta.db_table
        query = (
            "WITH RECURSIVE children (id) AS ("
            f"  SELECT {table_name}.id FROM {table_name} WHERE id = {self.pk}"
            "  UNION ALL"
            f"  SELECT {table_name}.id FROM children, {table_name}"
            f"  WHERE {table_name}.parent_id = children.id"
            ")"
            f" SELECT {table_name}.id"
            f" FROM {table_name}, children WHERE children.id = {table_name}.id"
        )
        if not include_self:
            query += f" AND {table_name}.id != {self.pk}"
        return Nationality.objects.filter(
            pk__in=[nationality.id for nationality in Nationality.objects.raw(query)]
        )


class PublicAthleteResultsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(alias_of=None)


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
    alias_of = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, default=None,
                                 related_name='aliases')

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    objects = PublicAthleteResultsManager()
    objects_with_aliases = models.Manager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('athlete-overview', args=[self.slug])

    def get_total_points(self):
        events = Event.objects.filter(use_points_in_athlete_total=True)
        total_points = 0
        for event in events:
            result = IndividualResult.public_objects.filter(event=event, athlete=self).aggregate(Max('points'))
            if result['points__max'] is not None:
                total_points += result['points__max']
        return round(total_points, 2)

    def get_personal_bests(self):
        events = Event.objects.filter(use_points_in_athlete_total=True)
        personal_bests = []
        for event in events:
            personal_best = IndividualResult.public_objects.filter(event=event, athlete=self).order_by('time').first()
            if personal_best:
                personal_bests.append(personal_best)
        return personal_bests

    def get_competitions(self, year=None):
        previous_best = IndividualResult.public_objects.filter(athlete=OuterRef('athlete'),
                                                               event=OuterRef('event'),
                                                               competition__date__lt=OuterRef('competition__date'),
                                                               disqualified=False,
                                                               did_not_start=False,
                                                               withdrawn=False,
                                                               time__isnull=False)

        individual_results = IndividualResult.public_objects.filter(athlete=self)
        individual_results = individual_results.select_related('event', 'athlete')
        individual_results = individual_results.prefetch_related('individualresultsplit_set')

        individual_results = individual_results.annotate(previous_best=Subquery(previous_best.values('time')[:1]))
        individual_results = individual_results.annotate(change=F('time') - F('previous_best'))

        if year is not None:
            individual_results = individual_results.filter(competition__date__year=year)
        competitions = individual_results.values('competition_id')
        competitions = Competition.objects.order_by('-date').prefetch_related(
            Prefetch('individual_results', queryset=individual_results, to_attr='athlete_results')
        ).filter(pk__in=competitions)
        return competitions

    def get_last_competition_date(self):
        return IndividualResult.public_objects.filter(athlete=self).aggregate(Max('competition__date'))[
            'competition__date__max']

    def get_next_competition_year(self, current_year):
        result = IndividualResult.public_objects.filter(athlete=self,
                                                        competition__date__year__gt=current_year).order_by(
            'competition__date').first()
        if result is not None:
            return result.competition.date.year
        return None

    def get_previous_competition_year(self, current_year):
        result = IndividualResult.public_objects.filter(athlete=self,
                                                        competition__date__year__lt=current_year).order_by(
            '-competition__date').first()
        if result is not None:
            return result.competition.date.year

    def count_results(self):
        return IndividualResult.public_objects.filter(athlete=self).count()

    def count_competitions(self):
        return IndividualResult.public_objects.filter(athlete=self).values_list('competition',
                                                                                flat=True).distinct().count()

    @classmethod
    def search(cls, query):
        athletes = Athlete.objects

        athletes = athletes.annotate(
            similarity=TrigramSimilarity('name', query)
        ).filter(similarity__gt=0.25).order_by('-similarity')

        return athletes


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
    slug = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.name

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
            if gender == 'men':
                gender = 1
            else:
                gender = 2
        if competition is None:
            query_set = IndividualResult.public_objects.filter(event=self, athlete__gender=gender, disqualified=False)
        else:
            query_set = IndividualResult.objects.filter(event=self, athlete__gender=gender, competition=competition)
            max_round = \
                IndividualResult.objects.filter(event=self, athlete__gender=gender,
                                                competition=competition).aggregate(
                    Max('round'))['round__max']
            query_set = query_set.filter(round=max_round)

        query_set = query_set.select_related('athlete')
        query_set = query_set.prefetch_related('athlete__nationalities', 'individualresultsplit_set')
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
    EXTRA_TIME = 5
    STATUS_OPTIONS = (
        (SCHEDULED, 'Scheduled for import'),
        (IMPORTED, 'Imported'),
        (UNABLE_TO_IMPORT, 'Unable to import'),
        (WANTED, 'Wanted'),
        (EXTRA_TIME, 'Extra time competition')
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

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    prepopulated_fields = {"slug": ("name",)}

    def __str__(self):
        if self.name:
            return self.name
        return 'unknown ' + str(self.pk)

    def get_athlete_count(self):
        return IndividualResult.public_objects.filter(competition=self).values('athlete').distinct().count()

    def get_result_count(self):
        return IndividualResult.public_objects.filter(competition=self).count()

    def get_absolute_url(self):
        return reverse('competition-overview', args=[self.slug])

    def get_athletes(self):
        return Athlete.objects.filter(
            pk__in=IndividualResult.public_objects.filter(competition=self).values('athlete').distinct())

    def is_fully_labeled(self):
        return Athlete.objects.filter(nationalities=None,
                                      pk__in=IndividualResult.public_objects.filter(competition=self).values(
                                          'athlete').distinct()).count() < 1

    def is_imported(self):
        return self.status == self.IMPORTED

    def get_unlabeled_athletes(self):
        athlete_ids = IndividualResult.public_objects.filter(competition=self).values('athlete').distinct()
        return Athlete.objects.filter(pk__in=athlete_ids, nationalities=None).all()

    def count_unlabeled_athletes(self):
        athlete_ids = IndividualResult.public_objects.filter(competition=self).values('athlete').distinct()
        return Athlete.objects.filter(pk__in=athlete_ids, nationalities=None).count()

    def get_file_url(self):
        return settings.COMPETITIONS_BUCKET_URL + self.file_name

    @classmethod
    def search(cls, query):
        competitions = Competition.objects
        vector = SearchVector('name') + SearchVector('location')
        query = SearchQuery(query)

        competitions = competitions.annotate(search=vector).filter(search=query)
        competitions = competitions.annotate(rank=SearchRank(vector, query)).order_by('-rank')
        competitions = competitions.filter(~Q(status=Competition.EXTRA_TIME))

        return competitions


class PublicIndividualResultsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(competition__is_concept=False,
                                             competition__status=Competition.IMPORTED,
                                             extra_analysis_time_by=None)

    def only_valid_results(self):
        qs = self.get_queryset()
        qs = qs.filter(disqualified=False, did_not_start=False, withdrawn=False, time__isnull=False)
        return qs


class IndividualResult(models.Model):
    athlete = ForeignKey(Athlete, on_delete=models.CASCADE)
    event = ForeignKey(Event, on_delete=models.CASCADE)
    competition = ForeignKey(Competition, on_delete=models.CASCADE,
                             related_name='individual_results',
                             related_query_name='individual_results')
    time = models.DurationField(blank=True, null=True)
    points = models.IntegerField(default=0)
    original_line = models.CharField(max_length=200, null=True, default=None)
    round = models.IntegerField(default=0)
    disqualified = models.BooleanField(default=False)
    did_not_start = models.BooleanField(default=False)
    withdrawn = models.BooleanField(default=False)

    extra_analysis_time_by = ForeignKey(User, on_delete=models.CASCADE, null=True, default=None, blank=True)

    objects = models.Manager()
    public_objects = PublicIndividualResultsManager()

    class Meta:
        ordering = ['time']

    def __str__(self):
        return self.athlete.name + ' ' + self.event.name + ' ' + str(self.time)

    def calculate_points(self):
        record = EventRecord.objects.filter(gender=self.athlete.gender, event=self.event).first()
        if self.disqualified or self.did_not_start or self.withdrawn or self.time is None or not record:
            return
        self.points = calculate_points(record.time.total_seconds() * 100, self.time.total_seconds() * 100)
        self.save()

    @staticmethod
    def find_fastest_by_athlete_and_event(athlete, event, analysis_group):
        qs = IndividualResult.objects.filter(athlete=athlete, event=event).order_by('time')
        qs = qs.filter(Q(extra_analysis_time_by=analysis_group.creator) | Q(extra_analysis_time_by=None))
        if analysis_group.simulation_date_from:
            qs = qs.filter(competition__date__gte=analysis_group.simulation_date_from)
        return qs.first()


class IndividualResultSplit(models.Model):
    class Meta:
        ordering = ('distance', 'time')

    individual_result = ForeignKey(IndividualResult, on_delete=models.CASCADE)
    time = models.DurationField()
    distance = models.IntegerField(default=0)


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
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
