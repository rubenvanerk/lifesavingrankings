from django.contrib import admin
from analysis.models import *


@admin.register(AnalysisGroup)
class AnalysisGroupAdmin(admin.ModelAdmin):
    fields = ['name', 'creator', 'public', 'athletes']
    list_display = ['name', 'creator', 'public', 'athlete_count']
    list_filter = ['public', 'creator']
    search_fields = ['name']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(athlete_count=Count('athletes'))
        return qs

    def athlete_count(self, country_instance):
        return country_instance.athlete_count
    athlete_count.admin_order_field = 'athlete_count'


@admin.register(SpecialResult)
class SpecialResultAdmin(admin.ModelAdmin):
    list_display = ['event', 'time_formatted', 'special_result_group']
    list_filter = ['special_result_group']


admin.site.register(SpecialResultGroup)