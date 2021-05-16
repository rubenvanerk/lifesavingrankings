from django.contrib import admin
from django.db.models import Count

from rankings.models import *


class EmptyAthleteFilter(admin.SimpleListFilter):
    title = 'Athletes without results'
    parameter_name = 'empty'

    def lookups(self, request, model_admin):
        return (
            ('without', 'Without'),
            ('with', 'With')
        )

    def queryset(self, request, queryset):
        if self.value() == 'without':
            return queryset.annotate(num_results=Count('individualresult')).exclude(num_results__gt=0)
        if self.value() == 'with':
            return queryset.filter(individualresult__count__gt=0)
        return queryset


class AthleteCountryFilter(admin.SimpleListFilter):
    title = 'Country'
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        lookups = []
        countries = Country.objects.annotate(athlete_count=Count('nationalities')).exclude(athlete_count=0).order_by('name')
        for country in countries:
            lookups.append((country.id, country.name))
        return lookups

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(nationalities__in=self.value())
        return queryset


class CompetitionCountryFilter(admin.SimpleListFilter):
    title = 'Country'
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        lookups = []
        countries = Country.objects.annotate(competition_count=Count('competition')).exclude(competition_count=0).order_by('name')
        for country in countries:
            lookups.append((country.id, country.name))
        return lookups

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(country=self.value())
        return queryset


@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    fields = ['name', 'slug', 'year_of_birth', 'gender', 'nationalities']
    list_display = ['name', 'year_of_birth', 'gender', 'result_count']
    list_filter = ['gender', EmptyAthleteFilter, AthleteCountryFilter]
    search_fields = ['name', 'year_of_birth']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(result_count=Count('individualresult'))
        return qs

    def result_count(self, athlete_instance):
        return athlete_instance.result_count
    result_count.admin_order_field = 'result_count'


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country', 'date', 'end_date', 'status', 'result_count']
    list_filter = ['status', 'date', CompetitionCountryFilter]
    search_fields = ['name', 'city', 'country__name']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(result_count=Count('individual_results'))
        return qs

    def result_count(self, country_instance):
        return country_instance.result_count
    result_count.admin_order_field = 'result_count'


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'lenex_code', 'athlete_count']
    search_fields = ['name', 'parent', 'lenex_code']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(athlete_count=Count('nationalities'))
        return qs

    def athlete_count(self, country_instance):
        return country_instance.athlete_count
    athlete_count.admin_order_field = 'athlete_count'


@admin.register(EventRecord)
class EventRecordAdmin(admin.ModelAdmin):
    list_display = ['event', 'gender', 'time_formatted']
    list_filter = ['gender', 'event__type']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'use_points_in_athlete_total']
    list_filter = ['type', 'use_points_in_athlete_total']


@admin.register(IndividualResult)
class IndividualResultAdmin(admin.ModelAdmin):
    fields = ['athlete', 'event', ('time', 'reaction_time'), 'competition', ('heat', 'lane', 'round', 'points'),
              ('disqualified', 'did_not_start', 'withdrawn')]
    list_display = ['athlete', 'event', 'time_formatted', 'competition']
    list_filter = ['event', 'disqualified', 'did_not_start', 'withdrawn']
    search_fields = ['athlete__name', 'competition__name']


@admin.register(RelayOrder)
class RelayOrderAdmin(admin.ModelAdmin):
    list_display = ['segment', 'event', 'index']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'participant_count']
    search_fields = ['name']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(participant_count=Count('participation'))
        return qs

    def participant_count(self, team_instance):
        return team_instance.participant_count
    participant_count.admin_order_field = 'participant_count'
