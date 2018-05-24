from django.contrib.auth.decorators import user_passes_test
from django.db.models import Min, Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView
from .models import *
from django.http import Http404, HttpResponseRedirect
from .forms import *


class FrontPageRecords(ListView):
    model = IndividualResult

    def get_queryset(self):
        qs = super(FrontPageRecords, self).get_queryset().filter(event__type=1)
        athletes = Athlete.objects.all

        men = qs.filter(athlete__gender=1)
        men = men.values('athlete__first_name', 'athlete__last_name', 'athlete__id', 'event__name', 'event__id',
                         'athlete__slug')
        men = men.annotate(time=Min('time')).order_by('event_id', 'time')

        women = qs.filter(athlete__gender=2)
        women = women.values('athlete__first_name', 'athlete__last_name', 'athlete__id', 'event__name', 'event__id',
                             'athlete__slug')
        women = women.annotate(time=Min('time')).order_by('event_id', 'time')

        result = {'men': best_result_per_event(men), 'women': best_result_per_event(women), 'times': qs,
                  'athletes': athletes}
        return result

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['athlete_count'] = Athlete.objects.all().count()
        context['result_count'] = IndividualResult.objects.all().count()
        return context

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
    athlete = None

    def get_athlete(self):
        if self.athlete is not Athlete:
            slug = self.kwargs.get('slug')
            self.athlete = Athlete.objects.filter(slug=slug).first()
            if not self.athlete:
                raise Http404
        return self.athlete

    def get_queryset(self):
        result = {}
        athlete = self.get_athlete()

        qs = IndividualResult.find_by_athlete(athlete).filter(event__type=1)
        qs = qs.values('event__name', 'event_id')
        qs = qs.annotate(time=Min('time'))
        result['individual'] = qs.order_by('event_id')

        qs = IndividualResult.find_by_athlete(athlete).filter(event__type=2)
        qs = qs.values('event__name', 'event_id')
        qs = qs.annotate(time=Min('time'))
        result['relay'] = qs.order_by('event_id')

        return result

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['athlete'] = self.get_athlete()
        return context

    template_name = 'rankings/personal_best.html'


def athlete_redirect_athlete_id_to_slug(request, athlete_id):
    athlete = Athlete.objects.filter(pk=athlete_id).first()
    if athlete is None:
        raise Http404
    return redirect(athlete, permanent=True)


def athlete_redirect_event_id_to_slug(request, slug, event_id):
    event = Event.objects.filter(pk=event_id).first()
    if event is None:
        raise Http404
    athlete = Athlete.objects.filter(slug=slug).first()
    if athlete is None:
        athlete = Athlete.objects.filter(pk=slug).first()
        if athlete is None:
            raise Http404
    return redirect(reverse('athlete-event', args=[athlete.slug, event.generate_slug()]), permanent=True)


def redirect_event_id_to_slug(request, event_id, gender):
    event = Event.objects.filter(pk=event_id).first()
    if event is None:
        raise Http404
    return redirect(reverse('best-by-event', args=[event.generate_slug(), gender]), permanent=True)


class EventByAthlete(ListView):
    model = IndividualResult
    athlete = None
    event = None

    def get_athlete(self):
        if self.athlete is not Athlete:
            self.athlete = Athlete.objects.get(slug=self.kwargs.get('slug'))
            if not self.athlete:
                raise Http404
        return self.athlete

    def get_event(self):
        if self.event is not Event:
            event_name = self.kwargs.get('event_name')
            self.event = Event.find_by_name(event_name)
            if not self.event:
                raise Http404
        return self.event

    def get_queryset(self):
        qs = super(EventByAthlete, self).get_queryset()

        athlete = self.get_athlete()
        event = self.get_event()

        qs = qs.filter(athlete=athlete)
        qs = qs.filter(event=event)
        qs = qs.values('time', 'competition__date', 'competition__name')
        qs = qs.order_by('time')
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['athlete'] = self.get_athlete()
        context['event'] = self.get_event()
        return context

    template_name = 'rankings/event_by_athlete.html'


@user_passes_test(lambda u: u.is_superuser)
def merge_athletes(request):
    if request.method == 'POST':

        form = MergeAthletesForm(request.POST)

        if form.is_valid():
            first_athlete = form['first_athlete'].value()
            second_athlete = form['second_athlete'].value()

            first_athlete_object = Athlete.objects.filter(slug=first_athlete).first()
            second_athlete_object = Athlete.objects.filter(slug=second_athlete).first()

            individual_results = IndividualResult.objects.filter(athlete=second_athlete_object)
            for result in individual_results:
                result.athlete = first_athlete_object
                result.save()

            second_athlete_object.delete()

            return HttpResponseRedirect(reverse('athlete-overview', args=[first_athlete]))

    else:
        form = MergeAthletesForm

        return render(request, 'rankings/merge_athletes.html', {'form': form})


class BestByEvent(ListView):
    model = IndividualResult
    event = None

    def get_event(self):
        if self.event is not Event:
            event_name = self.kwargs.get('event_name')
            self.event = Event.find_by_name(event_name)
            if not self.event:
                raise Http404
        return self.event

    def get_queryset(self):
        qs = super(BestByEvent, self).get_queryset()

        event = self.get_event()

        qs = qs.filter(event=event.id).order_by('time')

        gender = gender_name_to_int(self.kwargs.get('gender'))
        qs = qs.filter(athlete__gender=gender)

        qs = qs.values('athlete_id',
                       'athlete__first_name',
                       'athlete__last_name',
                       'athlete__year_of_birth',
                       'time',
                       'competition__date',
                       'competition__name',
                       'event__name',
                       'athlete__slug')

        return best_result_per_athlete(qs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['event'] = self.get_event()
        return context

    template_name = 'rankings/best_by_event.html'


class Search(ListView):
    model = Athlete

    def get_queryset(self):
        qs = super(Search, self).get_queryset()

        query = self.request.GET.get('athlete')

        parts = query.split(' ')

        if query and len(parts) > 1:
            qs = qs.filter(
                (Q(first_name__icontains=query) | Q(last_name__icontains=query))
                | (Q(first_name__icontains=parts[0]) | Q(last_name__icontains=parts[len(parts) - 1]))
            )
        else:
            qs = qs.filter((Q(first_name__icontains=query) | Q(last_name__icontains=query)))

        return qs

    def get_context_data(self, **kwargs):
        context = super(Search, self).get_context_data(**kwargs)
        context['query'] = self.request.GET.get('athlete')
        return context

    template_name = 'rankings/search.html'


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
