from django.contrib import admin
from rankings.models import *


class AthleteAdmin(admin.ModelAdmin):
    fields = ['name', 'slug', 'year_of_birth', 'gender', 'nationalities']
    list_display = ['name', 'year_of_birth', 'gender']
    list_filter = ['gender']


class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country', 'date', 'end_date', 'status']
    list_filter = ['status', 'date']


class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'lenex_code']


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
