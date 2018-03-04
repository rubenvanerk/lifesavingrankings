from django.db.models import Min
from django.views.generic import ListView, TemplateView
from .models import *
from django.http import Http404


class FrontPageRecords(ListView):
    model = IndividualResult

    def get_queryset(self):
        qs = super(FrontPageRecords, self).get_queryset().filter(event__type=1)
        athletes = Athlete.objects.all

        men = qs.filter(athlete__gender=1)
        men = men.values('athlete__first_name', 'athlete__last_name', 'athlete__id', 'event__name', 'event__id')
        men = men.annotate(time=Min('time')).order_by('event_id', 'time')

        women = qs.filter(athlete__gender=2)
        women = women.values('athlete__first_name', 'athlete__last_name', 'athlete__id', 'event__name', 'event__id')
        women = women.annotate(time=Min('time')).order_by('event_id', 'time')
        return best_result_per_event(men), best_result_per_event(women), qs, athletes

    template_name = 'rankings/front_page_records.html'


def best_result_per_event(qs):
    checked_events = []
    final_list = []
    for result in qs:
        if result.get('event__id') not in checked_events:
            checked_events.append(result.get('event__id'))
            final_list.append(result)
    return final_list


class PersonalBests(ListView):
    model = IndividualResult

    def get_queryset(self):
        result = {}
        athlete_id = self.kwargs.get('athlete_id')
        athlete = Athlete.objects.get(pk=athlete_id)
        if not athlete:
            raise Http404
        qs = IndividualResult.find_by_athlete(athlete).filter(event__type=1)
        qs = qs.values('event__name', 'athlete__first_name', 'athlete__last_name', 'athlete__gender', 'athlete_id',
                       'event_id')
        qs = qs.annotate(time=Min('time'))
        result['individual'] = qs
        qs = IndividualResult.find_by_athlete(athlete).filter(event__type=2)
        qs = qs.values('event__name', 'athlete__first_name', 'athlete__last_name', 'athlete__gender', 'athlete_id',
                       'event_id')
        qs = qs.annotate(time=Min('time'))
        result['relay'] = qs
        return result

    template_name = 'rankings/personal_best.html'


class EventByAthlete(ListView):
    model = IndividualResult

    def get_queryset(self):
        qs = super(EventByAthlete, self).get_queryset()
        athlete = Athlete.objects.get(pk=self.kwargs.get('athlete_id'))
        event = Event.objects.get(pk=self.kwargs.get('event_id'))
        qs = qs.filter(athlete=athlete)
        qs = qs.filter(event=event)
        qs = qs.values('event__name', 'athlete_id', 'athlete__first_name', 'athlete__last_name', 'athlete__gender',
                       'time', 'competition__date', 'competition__name')
        qs = qs.order_by('time')
        return qs

    template_name = 'rankings/event_by_athlete.html'


class BestByEvent(ListView):
    model = IndividualResult

    def get_queryset(self):
        qs = super(BestByEvent, self).get_queryset()

        event_id = self.kwargs.get('event_id')
        qs = qs.filter(event=event_id).order_by('time')

        gender = gender_name_to_int(self.kwargs.get('gender'))
        qs = qs.filter(athlete__gender=gender)

        qs = qs.values('athlete_id',
                       'athlete__first_name',
                       'athlete__last_name',
                       'athlete__year_of_birth',
                       'time',
                       'competition__date',
                       'competition__name',
                       'event__name')

        return best_result_per_athlete(qs)

    template_name = 'rankings/best_by_event.html'


def best_result_per_athlete(qs):
    checked_athletes = []
    final_list = []
    for result in qs:
        if result.get('athlete_id') not in checked_athletes:
            checked_athletes.append(result.get('athlete_id'))
            final_list.append(result)

    return final_list


def get_top_results_by_athlete_and_event(event_name, gender):
    qs = IndividualResult.objects.filter(athlete__gender=gender)
    event = Event.find_by_name(event_name)
    qs = qs.filter(event=event).order_by('time')

    qs = qs.values('athlete_id',
                   'athlete__first_name',
                   'athlete__last_name',
                   'athlete__year_of_birth',
                   'time',
                   'competition__date',
                   'competition__name',
                   'event__name')
    return qs


def gender_name_to_int(gender):
    if gender == 'men':
        return 1
    elif gender == 'women':
        return 2
    else:
        raise Http404




