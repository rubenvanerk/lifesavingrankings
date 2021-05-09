import django_tables2 as tables
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django_tables2 import A

from analysis.models import AnalysisGroup
from rankings.models import IndividualResult
from rankings.templatetags.datetime_filter import format_time


class DateColumn(tables.Column):
    def render(self, value):
        return value.strftime("%b. %d, %Y")


class TimeColumn(tables.Column):
    def render(self, value):
        return format_time(value)


class ExtraTimesTable(tables.Table):
    class Meta:
        model = IndividualResult
        fields = {'athlete', 'event', 'time', 'competition__date'}
        sequence = ('athlete', 'event', 'time', 'competition__date')

    competition__date = DateColumn()
    time = TimeColumn()
    athlete = tables.LinkColumn('athlete-overview', args=[A('athlete__slug')])
    actions = tables.TemplateColumn(verbose_name='Actions',
                                    template_name='columns/result_actions.html',
                                    orderable=False)


class AnalysisGroupTable(tables.Table):
    class Meta:
        model = AnalysisGroup
        fields = {'pk', 'name', 'athlete_count', 'actions'}
        sequence = ('pk', 'name', 'athlete_count', 'actions')

    pk = tables.Column(verbose_name='ID')
    actions = tables.TemplateColumn(verbose_name='Actions',
                                    template_name='columns/analysisgroup_actions.html',
                                    orderable=False)
    athlete_count = tables.Column(empty_values=())

    def render_athlete_count(self, record):
        return record.athletes.count()

    def order_athlete_count(self, queryset, is_descending):
        queryset = queryset.annotate(
            athlete_count=Count('athletes')
        ).order_by(("-" if is_descending else "") + "athlete_count")
        return (queryset, True)
