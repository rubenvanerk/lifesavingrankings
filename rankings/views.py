import datetime
import json
import random

from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count, OuterRef, Exists, F, Window
from django.db.models.functions import Rank
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, TemplateView, DeleteView, DetailView
from django_tables2.views import SingleTableMixin, SingleTableView
from django_filters.views import FilterView
from rankings.functions import mk_int, try_parse_int
from .filters import CompetitionFilter
from .models import *
from django.http import Http404, HttpResponseRedirect, HttpResponse
from .forms import *
from .tables import CompetitionTable, TeamTable


class CompetitionListView(SingleTableMixin, FilterView):
    table_class = CompetitionTable
    template_name = "competition/list.html"
    ordering = ['-date']
    queryset = Competition.public_objects.filter(slug__isnull=False).all()
    model = Competition
    filterset_class = CompetitionFilter


class CompetitionDetail(TemplateView):
    template_name = 'competition/detail.html'

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise Http404
        competition_slug = self.kwargs.get('competition_slug')
        competition = Competition.public_objects.get(slug=competition_slug)
        nationality = Country.objects.get(pk=request.POST['country'])

        for athlete in competition.get_unlabeled_athletes():
            athlete.nationalities.add(nationality)
            athlete.save()

        return HttpResponseRedirect(reverse('competition-detail', args=[competition.slug]))

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        competition_slug = self.kwargs.get('competition_slug')
        competition = (Competition.public_objects
                       .filter(slug=competition_slug)
                       .annotate(result_count=Count('individual_results'))).first()
        context['competition'] = competition

        if competition is None:
            raise Http404

        if competition.is_imported or self.request.user.is_superuser:
            event_ids = IndividualResult.objects.filter(competition=competition).values('event_id').distinct().all()
            events = Event.objects.filter(pk__in=event_ids).order_by('pk').all()
            context['events'] = {}
            limit = 8
            for event in events:
                context['events'][event.pk] = {}
                context['events'][event.pk]['object'] = event
                context['events'][event.pk]['results'] = {}
                context['events'][event.pk]['results']['men'] = event.get_top_by_competition_and_gender(
                    competition=competition,
                    gender=Athlete.MALE,
                    limit=limit)
                context['events'][event.pk]['results']['women'] = event.get_top_by_competition_and_gender(
                    competition=competition,
                    gender=Athlete.FEMALE,
                    limit=limit)
            if self.request.user.is_superuser:
                context['nationalities'] = Country.objects.filter(is_parent_country=False)
                context['unlabeled_athletes'] = competition.get_unlabeled_athletes()
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()

        competition = context['competition']
        if 'publish' in self.request.GET and self.request.GET['publish'] == 'true' and self.request.user.is_superuser:
            competition.is_concept = False
            competition.status = competition.IMPORTED
            competition.published_on = datetime.datetime.now()
            competition.save()
            return redirect(competition)
        if 'delete' in self.request.GET and self.request.GET['delete'] == 'true' and self.request.user.is_superuser:
            IndividualResult.objects.filter(competition=competition).delete()
            Participation.objects.filter(competition=competition).delete()
            competition.status = competition.SCHEDULED
            competition.save()
            return redirect('competition-list')

        return self.render_to_response(context)


class CompetitionEvent(TemplateView):
    template_name = 'competition/event.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        competition_slug = self.kwargs.get('competition_slug')
        competition = Competition.public_objects.get(slug=competition_slug)

        event_slug = self.kwargs.get('event_slug')
        event = Event.objects.get(slug=event_slug)
        gender = gender_name_to_int(self.kwargs.get('gender'))

        if competition is None or event is False:
            raise Http404

        results = IndividualResult.objects.filter(competition=competition, event=event,
                                                  athlete__gender=gender).order_by('-round', 'time')
        results = results.select_related('athlete')
        results = results.prefetch_related('athlete__nationalities', 'individualresultsplit_set')
        context['results'] = results

        context['competition'] = competition
        context['event'] = event
        context['gender'] = gender
        context['separator'] = results.filter(round__gt=0).count()

        return context


class EventList(TemplateView):
    template_name = 'event/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        events = Event.objects.filter(type__in=[Event.INDIVIDUAL, Event.RELAY_SEGMENT]).all().order_by('pk')
        context['events'] = {}
        limit = 3
        for event in events:
            context['events'][event.pk] = {}
            context['events'][event.pk]['object'] = event
            context['events'][event.pk]['results'] = {}

            results_men = IndividualResult.public_objects
            results_men = results_men.filter(event=event, athlete__gender=Athlete.MALE, disqualified=False) \
                .order_by('athlete', 'time') \
                .distinct('athlete')
            results_men = IndividualResult.public_objects.filter(id__in=results_men).prefetch_related('competition',
                                                                                                      'athlete__nationalities').order_by(
                'time')[:limit]
            context['events'][event.pk]['results']['men'] = results_men

            results_women = IndividualResult.public_objects.filter(event=event, athlete__gender=Athlete.FEMALE,
                                                                   disqualified=False).order_by(
                'athlete',
                'time').distinct(
                'athlete')
            results_women = IndividualResult.public_objects.filter(id__in=results_women).prefetch_related('athlete__nationalities',
                                                                                                          'competition').order_by(
                'time')[:limit]
            context['events'][event.pk]['results']['women'] = results_women
        return context


class EventAthletes(TemplateView):
    template_name = 'event/athletes.html'

    event = None

    def get_event(self):
        if self.event is not Event:
            slug = self.kwargs.get('event_slug')
            self.event = Event.objects.get(slug=slug)
            if not self.event:
                raise Http404
        return self.event

    def get_filter(self):
        result_filter = {
            'yob_start': int('0' + self.request.GET.get('yob_start', '0')),
            'yob_end': int('0' + self.request.GET.get('yob_end', '0')),
            'alltimes': self.request.GET.get('alltimes', '0')
        }
        if self.request.GET.get('nationality') or 0 > 0:
            result_filter['nationality'] = Country.objects.filter(
                pk=self.request.GET.get('nationality').strip()).first()

        if self.request.GET.get('rangestart'):
            result_filter['date_range_start'] = datetime.datetime.strptime(self.request.GET.get('rangestart'),
                                                                           settings.DATE_INPUT_FORMAT).date()
        if self.request.GET.get('rangeend'):
            result_filter['date_range_end'] = datetime.datetime.strptime(self.request.GET.get('rangeend'),
                                                                         settings.DATE_INPUT_FORMAT).date()

        lowest_year_of_birth = Athlete.objects.aggregate(Min('year_of_birth'))['year_of_birth__min']
        highest_year_of_birth = Athlete.objects.aggregate(Max('year_of_birth'))['year_of_birth__max']
        result_filter['year_of_birth_range'] = range(lowest_year_of_birth, highest_year_of_birth)
        result_filter['nationalities'] = Country.objects.all()

        result_filter['enabled'] = self.request.GET.get('yob_end') or self.request.GET.get(
            'yob_start') or self.request.GET.get('rangestart') or self.request.GET.get(
            'rangeend') or self.request.GET.get('nationality') or self.request.GET.get('alltimes')

        return result_filter

    def get_context_data(self, **kwargs):
        context = super(EventAthletes, self).get_context_data()
        event = self.get_event()
        gender = gender_name_to_int(self.kwargs.get('gender'))
        result_filter = self.get_filter()

        if 'alltimes' in result_filter and result_filter['alltimes'] == 'on':
            results = IndividualResult.public_objects.only_valid_results().filter(event=event, athlete__gender=gender)
            results = results.annotate(
                rank=Window(
                    expression=Rank(),
                    order_by=F('time').asc()
                ),
            )
            if 'date_range_start' in result_filter:
                results = results.filter(competition__date__gte=result_filter['date_range_start'])
            if 'date_range_end' in result_filter:
                results = results.filter(competition__date__lte=result_filter['date_range_end'])
            if 'nationality' in result_filter and type(result_filter['nationality']) is Country:
                results = results.filter(
                    athlete__nationalities__in=result_filter['nationality'].get_all_children(include_self=True))
            if 'yob_start' in result_filter and result_filter['yob_start'] > 0:
                results = results.filter(athlete__year_of_birth__gte=result_filter['yob_start'])

            if 'yob_end' in result_filter and result_filter['yob_end'] > 0:
                results = results.filter(athlete__year_of_birth__lte=result_filter['yob_end'])
            results = results.select_related('athlete', 'competition')
            results = results.prefetch_related('athlete__nationalities')
        else:
            athletes = Athlete.objects.filter(gender=gender)

            athlete_results = IndividualResult.public_objects.only_valid_results().filter(
                athlete=OuterRef('pk'),
                event=event
            )

            if 'date_range_start' in result_filter:
                athlete_results = athlete_results.filter(competition__date__gte=result_filter['date_range_start'])
            if 'date_range_end' in result_filter:
                athlete_results = athlete_results.filter(competition__date__lte=result_filter['date_range_end'])

            athletes = athletes.filter(Exists(athlete_results))

            if 'nationality' in result_filter and type(result_filter['nationality']) is Country:
                athletes = athletes.filter(
                    nationalities__in=result_filter['nationality'].get_all_children(include_self=True))

            if 'yob_start' in result_filter and result_filter['yob_start'] > 0:
                athletes = athletes.filter(year_of_birth__gte=result_filter['yob_start'])

            if 'yob_end' in result_filter and result_filter['yob_end'] > 0:
                athletes = athletes.filter(year_of_birth__lte=result_filter['yob_end'])

            personal_best_query = IndividualResult.public_objects.only_valid_results().filter(event=event,
                                                                                              athlete=OuterRef(
                                                                                                  'pk')).values('time')
            if 'date_range_start' in result_filter:
                personal_best_query = personal_best_query.filter(
                    competition__date__gte=result_filter['date_range_start'])
            if 'date_range_end' in result_filter:
                personal_best_query = personal_best_query.filter(competition__date__lte=result_filter['date_range_end'])

            athletes = athletes.annotate(personal_best=personal_best_query[:1])

            athletes = athletes.order_by('personal_best')

            athletes = athletes.annotate(
                rank=Window(
                    expression=Rank(),
                    order_by=F('personal_best').asc()
                ),
            )

            results_qs = IndividualResult.public_objects.only_valid_results().filter(event=event)
            if 'date_range_start' in result_filter:
                results_qs = results_qs.filter(competition__date__gte=result_filter['date_range_start'])
            if 'date_range_end' in result_filter:
                results_qs = results_qs.filter(competition__date__lte=result_filter['date_range_end'])
            athletes = athletes.prefetch_related(Prefetch('individualresult_set', queryset=results_qs))
            athletes = athletes.prefetch_related('individualresult_set__competition', 'nationalities')

            results = athletes

        per_page = 25
        paginator = Paginator(results, per_page)
        page_number = self.request.GET.get('page', 1)
        context['page_obj'] = paginator.get_page(page_number)
        context['paginator'] = paginator
        context['gender'] = self.kwargs.get('gender')
        context['event'] = event
        context['filter'] = result_filter
        return context


class Search(ListView):
    model = Athlete

    def get_context_data(self, **kwargs):
        context = super(Search, self).get_context_data(**kwargs)

        query = self.request.GET.get('athlete').strip()

        if not query:
            context['search_results'] = {}
            context['query'] = query
            return context

        athletes = Athlete.search(query)

        reported = try_parse_int(self.request.GET.get('reported'))
        message = ''
        success = False
        if reported == 0:
            success = False
            message = 'Select at least 2 athletes to report'
        elif reported == 1:
            message = 'Duplicate athletes reported. Thanks!'
            success = True
        context['message'] = message
        context['success'] = success

        context['search_results'] = athletes
        context['query'] = query
        return context

    def post(self, request, *args, **kwargs):
        athletes = Athlete.objects.filter(pk__in=request.POST.getlist('duplicates'))
        if athletes.count() < 2:
            return HttpResponseRedirect(
                reverse('search') + '?athlete=' + self.request.GET.get('athlete').strip() + '&reported=0')
        merge_request = MergeRequest.objects.create()
        for athlete in athletes:
            merge_request.athletes.add(athlete)
        merge_request.save()
        if request.user.is_staff:
            return HttpResponseRedirect(reverse('merge-request-detail', kwargs={'pk': merge_request.pk}))
        else:
            return HttpResponseRedirect(
                reverse('search') + '?athlete=' + self.request.GET.get('athlete').strip() + '&reported=1')

    template_name = 'athlete/search.html'


class AthleteDetail(TemplateView):
    athlete = None

    def dispatch(self, request, *args, **kwargs):
        athlete = self.get_athlete()
        if athlete.slug != self.kwargs.get('athlete_slug'):
            return HttpResponseRedirect(reverse('athlete-detail', args=(athlete.slug,)))
        return super(AthleteDetail, self).dispatch(request, *args, **kwargs)

    def get_athlete(self):
        if type(self.athlete) is not Athlete:
            slug = self.kwargs.get('athlete_slug')
            self.athlete = Athlete.objects_with_aliases.get(slug=slug)
            if not self.athlete:
                raise Http404
            if self.athlete.alias_of:
                self.athlete = self.athlete.alias_of
        return self.athlete

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        nationality = Country.objects.get(pk=request.POST['country'])
        athlete = self.get_athlete()
        if athlete.nationalities.filter(pk=nationality.pk).exists():
            athlete.nationalities.remove(nationality)
        else:
            athlete.nationalities.add(nationality)
        athlete.save()
        context['athlete'] = athlete
        return super(TemplateView, self).render_to_response(context)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AthleteDetail, self).get_context_data(**kwargs)

        athlete = self.get_athlete()

        context['personal_bests'] = {}

        qs = IndividualResult.public_objects.filter(athlete=athlete) \
            .filter(event__type=Event.INDIVIDUAL, disqualified=False) \
            .order_by('event', 'time').distinct('event')
        context['personal_bests']['individual'] = IndividualResult.public_objects.filter(id__in=qs).select_related(
            'competition', 'event')

        qs = IndividualResult.public_objects.filter(athlete=athlete) \
            .filter(event__type=Event.RELAY_SEGMENT, disqualified=False) \
            .order_by('event', 'time').distinct('event')
        context['personal_bests']['relay'] = IndividualResult.public_objects.filter(id__in=qs).select_related(
            'competition', 'event')

        context['athlete'] = athlete
        if self.request.user.is_staff:
            context['nationalities'] = Country.objects.filter(is_parent_country=False)
            context['all_results'] = IndividualResult.public_objects.filter(athlete=athlete).exclude(original_line__isnull=True)
        return context

    template_name = 'athlete/detail.html'


class AthleteEvent(ListView):
    model = IndividualResult
    athlete = None
    event = None

    def get_athlete(self):
        if type(self.athlete) is not Athlete:
            self.athlete = Athlete.objects.get(slug=self.kwargs.get('athlete_slug'))
            if not self.athlete:
                raise Http404
        return self.athlete

    def get_event(self):
        if type(self.event) is not Event:
            self.event = Event.objects.get(slug=self.kwargs.get('event_slug'))
            if not self.event:
                raise Http404
        return self.event

    def get_queryset(self):
        qs = super(AthleteEvent, self).get_queryset()

        athlete = self.get_athlete()
        event = self.get_event()

        qs = qs.filter(athlete=athlete, event=event, disqualified=False, did_not_start=False, withdrawn=False,
                       time__isnull=False)
        qs = qs.select_related('competition')
        qs = qs.prefetch_related('individualresultsplit_set')
        if self.request.user.is_authenticated:
            user = self.request.user
            qs = qs.filter(Q(extra_analysis_time_by=user) | Q(extra_analysis_time_by=None))
        else:
            qs = qs.filter(extra_analysis_time_by=None)
        qs = qs.order_by('time')
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['athlete'] = athlete = self.get_athlete()
        context['event'] = event = self.get_event()
        results_ordered_by_date = self.get_queryset().order_by('competition__date')

        # if 2 results on 1 day, only show fastest
        previous_result = None
        for i, result in enumerate(results_ordered_by_date):
            if previous_result is not None and result.competition.date == previous_result.competition.date:
                if previous_result.time > result.time:
                    results_ordered_by_date = results_ordered_by_date.exclude(pk=previous_result.pk)
                    previous_result = result
                else:
                    results_ordered_by_date = results_ordered_by_date.exclude(pk=result.pk)
            else:
                previous_result = result

        context['results_ordered_by_date'] = results_ordered_by_date
        context['fastest_time'] = IndividualResult.public_objects.filter(athlete=athlete, event=event,
                                                                         did_not_start=False,
                                                                         disqualified=False).aggregate(Min('time'))
        context['slowest_time'] = IndividualResult.public_objects.filter(athlete=athlete, event=event,
                                                                         did_not_start=False,
                                                                         disqualified=False).aggregate(Max('time'))
        return context

    template_name = 'athlete/event.html'


class AthleteTimeline(TemplateView):
    athlete = None
    template_name = 'athlete/timeline.html'

    def get_athlete(self):
        if type(self.athlete) is not Athlete:
            self.athlete = Athlete.objects.get(slug=self.kwargs.get('athlete_slug'))
            if not self.athlete:
                raise Http404
        return self.athlete

    def get_year(self):
        year = mk_int(self.request.GET.get('year'))
        if not year:
            year = self.get_athlete().get_last_competition_date().year
        return year

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['athlete'] = athlete = self.get_athlete()
        context['current_year'] = year = self.get_year()
        context['competitions'] = athlete.get_competitions(year)
        context['previous_year'] = athlete.get_previous_competition_year(year)
        context['next_year'] = athlete.get_next_competition_year(year)
        return context


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class MergeRequestListView(ListView):
    model = MergeRequest
    template_name = 'mergerequests/list.html'


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class MergeRequestDeleteView(DeleteView):
    model = MergeRequest
    template_name = 'mergerequests/confirm_delete.html'
    success_url = reverse_lazy('merge-request-list')


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class MergeRequestDetailView(DetailView):
    model = MergeRequest
    template_name = 'mergerequests/detail.html'

    def post(self, request, *args, **kwargs):
        merge_request = super().get_object()
        if not request.POST['main-athlete']:
            return HttpResponseRedirect(reverse('merge-request-detail', kwargs={'pk': merge_request.pk}))
        main_athlete = Athlete.objects.get(pk=request.POST['main-athlete'])
        for athlete in merge_request.athletes.all():
            if athlete == main_athlete:
                continue

            for result in athlete.individualresult_set.all():
                result.athlete = main_athlete
                result.save()

            for nationality in athlete.nationalities.all():
                main_athlete.nationalities.add(nationality)

            for alias in athlete.aliases.all():
                alias.alias_of = main_athlete

            for participation in athlete.participation_set.all():
                participation.athlete = main_athlete

            if not main_athlete.year_of_birth and athlete.year_of_birth:
                main_athlete.year_of_birth = athlete.year_of_birth

            if not main_athlete.gender and athlete.gender:
                main_athlete.gender = athlete.gender

            main_athlete.save()
            athlete.alias_of = main_athlete
            athlete.save()
        merge_request.delete()

        return HttpResponseRedirect(reverse('merge-request-list'))


class TeamListView(SingleTableView):
    model = Team
    table_class = TeamTable
    template_name = 'team/list.html'


class TeamDetailView(DetailView):
    model = Team
    template_name = 'team/detail.html'


class TeamCompetitionView(TemplateView):
    template_name = 'team/competition.html'

    def get_context_data(self, **kwargs):
        context = super(TeamCompetitionView, self).get_context_data(**kwargs)
        context['team'] = team = Team.objects.get(slug=kwargs.get('team_slug'))
        context['competition'] = competition = Competition.public_objects.get(slug=kwargs.get('competition_slug'))
        context['participations'] = Participation.objects.filter(team=team, competition=competition).select_related(
            'athlete')
        return context


@login_required
def add_result(request, athlete_slug):
    athlete = Athlete.objects.get(slug=athlete_slug)
    if athlete is None:
        raise Http404

    if request.method == 'POST':
        form = AddResultForm(request.POST)

        if form.is_valid():
            time = form.cleaned_data['time']
            date = form.cleaned_data['date']
            event = form.cleaned_data['event']

            competition = Competition()
            competition.date = date
            competition.is_concept = False
            competition.slug = None
            competition.location = 'Database'
            competition.type_of_timekeeping = 0
            competition.status = Competition.EXTRA_TIME
            competition.save()

            result = IndividualResult()
            result.time = time
            result.athlete = athlete
            result.competition = competition
            result.event = event
            result.extra_analysis_time_by = request.user
            result.save()
            result.calculate_points()

            return HttpResponseRedirect(reverse('athlete-event', args=(athlete_slug, event.slug)))
        else:
            return render(request, 'add_result.html', {'form': form, 'athlete': athlete})
    else:
        form = AddResultForm

        return render(request, 'add_result.html', {'form': form, 'athlete': athlete})


class IndividualResultDelete(DeleteView):
    model = IndividualResult
    success_url = reverse_lazy('home')
    template_name = 'extra_time_confirm_delete.html'

    def get_object(self, queryset=None):
        obj = super(IndividualResultDelete, self).get_object()
        self.success_url = reverse_lazy('athlete-detail', args=[obj.athlete.pk])
        if not obj.extra_analysis_time_by == self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        return self.request.GET.get('success_url', self.success_url)


def request_competition(request):
    if request.method == 'POST':
        form = RequestCompetitionForm(request.POST)

        if form.is_valid():
            competition_name = form['competition_name'].value()
            competition_date = form['competition_date'].value()
            your_email = form['your_email'].value()
            link_to_results = form['link_to_results'].value()
            location = form['location'].value()

            body = "Competition name: " + competition_name + "\n" \
                                                             "Competition date: " + competition_date + "\n" \
                                                                                                       "Link to results: " + link_to_results + "\n" \
                                                                                                                                               "Location: " + location + "\n" \
                                                                                                                                                                         "Request email: " + your_email

            send_mail(
                'Lifesaving Rankings competition request',
                body,
                'noreply@lifesavingrankings.com',
                ['ruben@lifesavingrankings.com'],
                fail_silently=False,
            )

            return render(request, 'request_competition.html', {'form': form, 'form_sent': True})
        else:
            return render(request, 'request_competition.html', {'form': form})
    else:
        form = RequestCompetitionForm

        return render(request, 'request_competition.html', {'form': form})


def api_search_athletes(request, query):
    athletes = Athlete.search(query)
    json_athletes = []
    for athlete in athletes:
        json_athletes.append({'name': athlete.name, 'value': str(athlete.pk)})
    response = {'success': True, 'results': json_athletes}
    return HttpResponse(json.dumps(response), content_type="text/json")


@user_passes_test(lambda u: u.is_staff)
def label_nationality(request, pk):
    athlete = Athlete.objects.filter(pk=pk).first()
    queue = Athlete.objects.filter(nationalities=None).annotate(num_results=Count('individualresult')).filter(
        num_results__gt=3).all()

    next_athlete = None
    if queue:
        next_athlete = random.choice(queue)
    if not athlete and next_athlete is not None:
        return HttpResponseRedirect(reverse('label-athlete', kwargs={'pk': next_athlete.pk}))

    if request.method == 'POST':
        nationality = Country.objects.get(pk=request.POST['country'])
        athlete.nationalities.add(nationality)
        athlete.save()
        return HttpResponseRedirect(reverse('label-athlete', kwargs={'pk': next_athlete.pk}))

    athlete_count = Athlete.objects.count()
    labeled_athletes = Athlete.objects.filter(~Q(nationalities=None)).count()
    progress = labeled_athletes / athlete_count * 100

    return render(request, 'label_nationality.html',
                  {'athlete': athlete, 'nationalities': Country.objects.filter(is_parent_country=False),
                   'athlete_count': athlete_count,
                   'labeled_athletes': labeled_athletes, 'progress': progress, 'next_athlete': next_athlete,
                   'queue': queue,
                   'all_results': IndividualResult.public_objects.filter(athlete=athlete)})


@user_passes_test(lambda u: u.is_superuser)
def recalculate_points(request):
    total_results = IndividualResult.objects.filter(event__type=1).count()
    print('Amount of results to calculate: ' + str(total_results))

    for index, result in enumerate(IndividualResult.objects.filter(event__type=1), start=1):
        result.calculate_points()
        if index % 100 == 0:
            print(str(index) + '/' + str(total_results))

    return HttpResponse('points calculated')


def report_duplicate(request):
    query = request.GET.get('query', '')
    send_mail(
        'Lifesaving Rankings duplicate athlete reported',
        'https://www.lifesavingrankings.com/rankings/search?athlete=' + query,
        'noreply@lifesavingrankings.com',
        ['ruben@lifesavingrankings.com'],
        fail_silently=False,
    )
    return HttpResponse('')


# Helper functions

def gender_name_to_int(gender):
    if gender == 'men':
        return 1
    elif gender == 'women':
        return 2
    else:
        raise Http404


# Redirects from old url format

def athlete_redirect_athlete_id_to_slug(request, athlete_id):
    athlete = Athlete.objects.get(pk=athlete_id)
    if athlete is None:
        raise Http404
    return redirect(athlete, permanent=True)


def athlete_redirect_event_id_to_slug(request, athlete_slug, event_id):
    event = Event.objects.get(pk=event_id)
    if event is None:
        raise Http404
    return redirect(reverse('athlete-event', args=[athlete_slug, event.slug]), permanent=True)


def redirect_event_id_to_slug(request, event_id, gender):
    event = Event.objects.get(pk=event_id)
    if event is None:
        raise Http404
    return redirect(reverse('best-by-event', args=[event.slug, gender]), permanent=True)
