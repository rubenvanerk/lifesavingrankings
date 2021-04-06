import django_tables2 as tables
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django_tables2 import A

from rankings.models import Competition, Team


class DateColumn(tables.Column):
    def render(self, value):
        return value.strftime("%b. %d, %Y")


class CompetitionTable(tables.Table):
    def __init__(self, *args, c1_name="", **kwargs):
        super().__init__(*args, **kwargs)
        self.base_columns['athlete_count'].verbose_name = 'Athlete count / status'

    class Meta:
        model = Competition
        fields = {'name', 'date', 'location'}
        sequence = ('name', 'date', 'location', 'athlete_count')

    date = DateColumn()
    athlete_count = tables.Column(empty_values=())

    def render_name(self, record):
        return format_html('<a href="%s">%s</a>' % (reverse('competition-overview', args={record.slug}), record.name))

    def render_athlete_count(self, record):
        return record.get_athlete_count() or record.get_status_display()

    def order_athlete_count(self, queryset, is_descending):
        queryset = queryset.annotate(
            athlete_count=Count('individual_results__athlete', distinct=True)
        ).order_by(("-" if is_descending else "") + "athlete_count")
        return (queryset, True)


class TeamTable(tables.Table):
    name = tables.LinkColumn('team-detail', args=[A('slug')])

    class Meta:
        model = Team
        fields = {'name'}
