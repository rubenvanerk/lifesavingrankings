from django.db.models import Min
from django.views.generic import ListView, TemplateView
from .models import *
from django.http import Http404
import numpy as numpy


class FrontPageRecords(ListView):
    model = IndividualResult

    def get_queryset(self):
        qs = super(FrontPageRecords, self).get_queryset()
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
        name = self.kwargs.get('name')
        athlete = Athlete.find_by_name(name)
        qs = IndividualResult.find_by_athlete(athlete)
        qs = qs.values('event__name', 'athlete__first_name', 'athlete__last_name', 'athlete__gender', 'athlete_id',
                       'event_id')
        qs = qs.annotate(time=Min('time'))
        return qs

    template_name = 'rankings/personal_best.html'


class EventByAthlete(ListView):
    model = IndividualResult

    def get_queryset(self):
        qs = super(EventByAthlete, self).get_queryset()
        athlete = Athlete.find_by_name(self.kwargs.get('athlete_name'))
        event = Event.find_by_name(self.kwargs.get('event_name'))
        qs = qs.filter(athlete=athlete)
        qs = qs.filter(event=event)
        qs = qs.values('event__name', 'athlete__first_name', 'athlete__last_name', 'athlete__gender', 'time',
                       'competition__date', 'competition__name')
        qs = qs.order_by('time')
        return qs

    template_name = 'rankings/event_by_athlete.html'


class BestByEvent(ListView):
    model = IndividualResult

    def get_queryset(self):
        qs = super(BestByEvent, self).get_queryset()

        event_name = self.kwargs.get('event_name')
        event = Event.find_by_name(event_name)
        qs = qs.filter(event=event).order_by('time')

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


class Analysis(TemplateView):
    template_name = 'rankings/analysis.html'

    def get_context_data(self, **kwargs):
        context = super(Analysis, self).get_context_data(**kwargs)
        gender = gender_name_to_int(self.kwargs.get('gender'))
        context['gender'] = gender
        context['results'] = self.get_top_results_by_athlete(gender)
        context['special_results'] = SpecialResult.objects.filter(gender=gender)
        context['events'] = Event.objects.all()
        return context

    def get_top_results_by_athlete(self, gender):
        events = Event.objects.all()
        athletes = Athlete.objects.filter(gender=gender)
        results = {}

        for athlete in athletes:
            individual_results = []
            for event in events:
                qs = IndividualResult.find_by_athlete_and_event(athlete, event)
                qs = qs.values('event__name',
                               'event_id')
                qs = qs.annotate(pb=Min('time'))
                individual_results.append(qs)
            results[athlete.id] = individual_results
        return results


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




