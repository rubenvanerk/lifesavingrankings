from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Min
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView, TemplateView
from .models import *
from django.http import Http404, HttpResponseRedirect
from .forms import *


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
        result['individual'] = qs.order_by('event_id')
        qs = IndividualResult.find_by_athlete(athlete).filter(event__type=2)
        qs = qs.values('event__name', 'athlete__first_name', 'athlete__last_name', 'athlete__gender', 'athlete_id',
                       'event_id')
        qs = qs.annotate(time=Min('time'))
        result['relay'] = qs.order_by('event_id')
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


@login_required
def merge_athletes(request):
    if request.method == 'POST':

        form = MergeAthletesForm(request.POST)

        if form.is_valid():
            first_athlete = form['first_athlete'].value()
            second_athlete = form['second_athlete'].value()

            first_athlete_object = Athlete.objects.get(pk=first_athlete)

            individual_results = IndividualResult.objects.filter(athlete=second_athlete)
            for result in individual_results:
                result.athlete = first_athlete_object
                result.save()

            second_athlete_object = Athlete.objects.get(pk=second_athlete)
            second_athlete_object.delete()

            return HttpResponseRedirect(reverse('athlete-overview', args=[first_athlete]))

    else:
        form = MergeAthletesForm

        return render(request, 'rankings/merge_athletes.html', {'form': form})


class BestByEvent(ListView):
    model = IndividualResult

    def get_queryset(self):
        qs = super(BestByEvent, self).get_queryset()

        event_id = self.kwargs.get('event_id')
        qs = qs.filter(event=event_id).order_by('time')

        gender = gender_name_to_int(self.kwargs.get('gender'))
        qs = qs.filter(athlete__gender=gender).order_by(event_id)

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


def gender_name_to_int(gender):
    if gender == 'men':
        return 1
    elif gender == 'women':
        return 2
    else:
        raise Http404
