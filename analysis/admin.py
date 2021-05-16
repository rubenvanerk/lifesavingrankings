from django.contrib import admin
from analysis.models import *


class AnalysisGroupAdmin(admin.ModelAdmin):
    fields = ['name', 'creator', 'public', 'athletes']
    list_display = ['name', 'creator', 'public']
    list_filter = ['public', 'creator']


class SpecialResultAdmin(admin.ModelAdmin):
    list_display = ['event', 'time_formatted', 'special_result_group']
    list_filter = ['special_result_group']


admin.site.register(AnalysisGroup, AnalysisGroupAdmin)
admin.site.register(SpecialResultGroup)
admin.site.register(SpecialResult, SpecialResultAdmin)
