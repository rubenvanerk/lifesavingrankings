import django_filters
from django.db.models import Q

from rankings.models import Competition


class CompetitionFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='search_name_and_location', label='')

    class Meta:
        model = Competition
        fields = ['q']

    def search_name_and_location(self, queryset, name, value):
        return Competition.objects.filter(
            Q(name__icontains=value) | Q(location__icontains=value)
        )