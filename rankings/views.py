from django.contrib.auth.decorators import user_passes_test, login_required
from django.db.models import Min, Q
from django.shortcuts import render, redirect
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

        men = qs.filter(athlete__gender=1, extra_analysis_time_by=None)
        men = men.values('athlete__name', 'athlete__id', 'event__name', 'event__id',
                         'athlete__slug')
        men = men.annotate(time=Min('time')).order_by('event_id', 'time')

        women = qs.filter(athlete__gender=2, extra_analysis_time_by=None)
        women = women.values('athlete__name', 'athlete__id', 'event__name', 'event__id',
                             'athlete__slug')
        women = women.annotate(time=Min('time')).order_by('event_id', 'time')

        result = {'genders': {'men': best_result_per_event(men), 'women': best_result_per_event(women)}, 'times': qs,
                  'athletes': athletes}
        return result

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['athlete_count'] = Athlete.objects.all().count()
        context['result_count'] = IndividualResult.objects.all().count()
        context['home'] = True
        context['last_added_competition'] = Competition.objects.filter(slug__isnull=False).order_by('-date').first()
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


class CompetitionOverview(TemplateView):
    template_name = 'rankings/competition_overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        competition_slug = self.kwargs.get('competition_slug')
        competition = Competition.objects.filter(slug=competition_slug).first()
        if competition is None:
            raise Http404
        if competition.is_concept and not self.request.user.is_superuser:
            raise Http404

        event_ids = IndividualResult.objects.filter(competition=competition).values('event_id').distinct().all()
        events = Event.objects.filter(pk__in=event_ids).order_by('pk').all()
        context['events'] = {}
        limit = 10
        for event in events:
            context['events'][event.name] = {}
            context['events'][event.name]['men'] = event.get_top_by_competition_and_gender(competition, 1, limit)
            context['events'][event.name]['women'] = event.get_top_by_competition_and_gender(competition, 2, limit)
        context['competition'] = competition
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()

        competition = context['competition']
        if 'publish' in self.request.GET and self.request.GET['publish'] == 'true' and self.request.user.is_superuser:
            competition.is_concept = False
            competition.save()
            return redirect(competition)
        if 'delete' in self.request.GET and self.request.GET['delete'] == 'true' and self.request.user.is_superuser:
            competition.delete()
            return redirect('competition-list')

        return self.render_to_response(context)


class CompetitionEvent(TemplateView):
    template_name = 'rankings/competition_event.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        competition_slug = self.kwargs.get('competition_slug')
        competition = Competition.objects.filter(slug=competition_slug).first()

        event_name = self.kwargs.get('event_name')
        event = Event.find_by_name(event_name)
        gender = gender_name_to_int(self.kwargs.get('gender'))

        if competition is None or event is False:
            raise Http404

        results = IndividualResult.objects.filter(competition=competition, event=event,
                                                  athlete__gender=gender).order_by('time').all()
        context['results'] = results

        context['competition'] = competition
        context['event'] = event
        context['gender'] = gender

        return context


class CompetitionListView(ListView):
    model = Competition
    ordering = ['-date']

    def get_queryset(self):
        qs = super(CompetitionListView, self).get_queryset()
        qs = qs.filter(slug__isnull=False)
        if not self.request.user.is_superuser:
            return qs.filter(is_concept=False)
        return qs


class EventOverview(TemplateView):
    template_name = 'rankings/event_overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        events = Event.objects.filter(type__in=[1, 2]).all().order_by('pk')
        context['events'] = {}
        limit = 3
        for event in events:
            context['events'][event.name] = {}
            results_men = IndividualResult.objects.filter(event=event, athlete__gender=1,
                                                          extra_analysis_time_by=None).order_by('time').all()
            context['events'][event.name]['men'] = best_result_per_athlete_v2(results_men, limit)
            results_women = IndividualResult.objects.filter(event=event, athlete__gender=2,
                                                            extra_analysis_time_by=None).order_by('time').all()
            context['events'][event.name]['women'] = best_result_per_athlete_v2(results_women, limit)
        return context


def best_result_per_athlete_v2(results, limit):
    checked_athletes = []
    final_list = []
    for result in results:
        if result.athlete not in checked_athletes:
            checked_athletes.append(result.athlete)
            final_list.append(result)
        if len(final_list) == limit:
            return final_list
    return final_list


def best_result_per_athlete(qs):
    checked_athletes = []
    final_list = []
    for result in qs:
        if result.get('athlete_id') not in checked_athletes:
            checked_athletes.append(result.get('athlete_id'))
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

        qs = IndividualResult.find_by_athlete(athlete).filter(event__type=1).filter(extra_analysis_time_by=None)
        qs = qs.values('event__name', 'event_id')
        qs = qs.annotate(time=Min('time'))
        result['individual'] = qs.order_by('event_id')

        qs = IndividualResult.find_by_athlete(athlete).filter(event__type=2).filter(extra_analysis_time_by=None)
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
        if self.request.user.is_authenticated:
            user = self.request.user
            qs = qs.filter(Q(extra_analysis_time_by=user) | Q(extra_analysis_time_by=None))
        else:
            qs = qs.filter(extra_analysis_time_by=None)
        qs = qs.values('time', 'competition__date', 'competition__name', 'competition__slug')
        qs = qs.order_by('time')
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['athlete'] = self.get_athlete()
        context['event'] = self.get_event()
        return context

    template_name = 'rankings/event_by_athlete.html'


@login_required
def add_result(request, athlete_slug, event_slug):
    athlete = Athlete.objects.filter(slug=athlete_slug).first()
    event = Event.find_by_name(event_slug)
    if athlete is None or event is False:
        raise Http404

    if request.method == 'POST':
        form = AddResultForm(request.POST)

        if form.is_valid():
            time = form['time'].value()
            date = form['date'].value()

            competition = Competition()
            competition.date = date
            competition.is_concept = False
            competition.slug = None
            competition.location = 'Database'
            competition.type_of_timekeeping = 0
            competition.save()

            result = IndividualResult()
            result.time = time
            result.athlete = athlete
            result.competition = competition
            result.event = event
            result.extra_analysis_time_by = request.user
            result.save()

            return HttpResponseRedirect(reverse('athlete-event', args=(athlete_slug, event_slug)))
        else:
            return render(request, 'rankings/add_result.html', {'form': form, 'athlete': athlete, 'event': event})
    else:
        form = AddResultForm

        return render(request, 'rankings/add_result.html', {'form': form, 'athlete': athlete, 'event': event})


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
        qs = qs.filter(extra_analysis_time_by=None)

        event = self.get_event()

        qs = qs.filter(event=event.id).order_by('time')

        gender = gender_name_to_int(self.kwargs.get('gender'))
        qs = qs.filter(athlete__gender=gender)

        qs = qs.values('athlete_id',
                       'athlete__name',
                       'athlete__year_of_birth',
                       'time',
                       'competition__date',
                       'competition__name',
                       'competition__slug',
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
