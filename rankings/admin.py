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


class AthleteAdmin(admin.ModelAdmin):
    fields = ['name', 'slug', 'year_of_birth', 'gender', 'nationalities']
    list_display = ['name', 'year_of_birth', 'gender', 'result_count']
    list_filter = ['gender', EmptyAthleteFilter]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(result_count=Count('individualresult'))
        return qs

    def result_count(self, athlete_instance):
        return athlete_instance.result_count
    result_count.admin_order_field = 'result_count'


class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country', 'date', 'end_date', 'status', 'result_count']
    list_filter = ['status', 'date']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(result_count=Count('individual_results'))
        return qs

    def result_count(self, country_instance):
        return country_instance.result_count
    result_count.admin_order_field = 'result_count'


class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'lenex_code', 'athlete_count']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(athlete_count=Count('nationalities'))
        return qs

    def athlete_count(self, country_instance):
        return country_instance.athlete_count
    athlete_count.admin_order_field = 'athlete_count'


class EventRecordAdmin(admin.ModelAdmin):
    list_display = ['event', 'gender', 'time_formatted']
    list_filter = ['gender']


class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'use_points_in_athlete_total']
    list_filter = ['type', 'use_points_in_athlete_total']


class IndividualResultAdmin(admin.ModelAdmin):
    fields = ['athlete', 'event', ('time', 'reaction_time'), 'competition', ('heat', 'lane', 'round', 'points'),
              ('disqualified', 'did_not_start', 'withdrawn')]
    list_display = ['athlete', 'event', 'time_formatted', 'competition']
    list_filter = ['event', 'disqualified', 'did_not_start', 'withdrawn']


class RelayOrderAdmin(admin.ModelAdmin):
    list_display = ['segment', 'event', 'index']


admin.site.register(Athlete, AthleteAdmin)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(EventRecord, EventRecordAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(IndividualResult, IndividualResultAdmin)
admin.site.register(RelayOrder, RelayOrderAdmin)
admin.site.register(Team)
