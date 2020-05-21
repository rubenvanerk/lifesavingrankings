import datetime
import functools
import itertools
from datetime import timedelta
from multiprocessing import Process
from time import sleep

import requests
from django.conf import settings

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied
from django.db.models import Min, Q
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DeleteView

from analysis.forms import ChooseFromDateForm, AnalysisGroupForm
from analysis.models import AnalysisGroup, GroupTeam, GroupEventSetup, GroupEvenSetupSegment, \
    SpecialResultGroup
from rankings.models import Event, Athlete, IndividualResult, RelayOrder


def get_top_results_by_athlete(gender=None, athletes=None, date=None, user=None):
    events = Event.objects.filter(type=Event.INDIVIDUAL, use_points_in_athlete_total=True).order_by('id')
    if athletes is None:
        athletes = Athlete.objects.filter(gender=gender)
    results = {}

    for athlete in athletes:
        individual_results = []
        for event in events:
            qs = IndividualResult.objects.filter(athlete=athlete, event=event, did_not_start=False, disqualified=False)
            if user is not None:
                qs = qs.filter(Q(extra_analysis_time_by=user) | Q(extra_analysis_time_by=None))
            if date is not None:
                qs = qs.filter(competition__date__gte=date)
            qs = qs.order_by('time')
            individual_results.append(qs.first())
        results[athlete.id] = individual_results
    return results


class AnalysisGroupListView(LoginRequiredMixin, ListView):
    model = AnalysisGroup

    def get_queryset(self):
        user = self.request.user
        qs = super(AnalysisGroupListView, self).get_queryset()
        if not self.request.user.is_superuser:
            qs = qs.filter(creator=user)
        return qs


class PublicAnalysisGroupListView(ListView):
    model = AnalysisGroup

    def get_queryset(self):
        qs = super(PublicAnalysisGroupListView, self).get_queryset().order_by('pk')
        qs = qs.filter(public=True)
        return qs

    def get_context_data(self, **kwargs):
        context = super(PublicAnalysisGroupListView, self).get_context_data()
        context['public'] = True
        return context


class AnalysisGroupUpdate(LoginRequiredMixin, UpdateView):
    model = AnalysisGroup
    form_class = AnalysisGroupForm
    success_url = reverse_lazy('private-group-list')

    def get_object(self, queryset=None):
        obj = super(AnalysisGroupUpdate, self).get_object()
        if obj.creator != self.request.user:
            raise PermissionDenied
        else:
            return obj


class AnalysisGroupDelete(LoginRequiredMixin, DeleteView):
    model = AnalysisGroup
    success_url = reverse_lazy('private-group-list')

    def get_object(self, queryset=None):
        obj = super(AnalysisGroupDelete, self).get_object()
        if obj.creator != self.request.user:
            raise PermissionDenied
        else:
            return obj


class AnalysisGroupCreate(LoginRequiredMixin, CreateView):
    model = AnalysisGroup
    form_class = AnalysisGroupForm
    success_url = reverse_lazy('private-group-list')

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super(AnalysisGroupCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(AnalysisGroupCreate, self).get_context_data()
        context['new_group'] = True
        return context


class IndividualAnalysis(TemplateView):
    template_name = 'analysis/individual_analysis.html'

    def get_context_data(self, **kwargs):
        context = super(IndividualAnalysis, self).get_context_data(**kwargs)
        analysis_group = AnalysisGroup.objects.get(pk=self.kwargs.get('pk'))
        if not analysis_group.public and analysis_group.creator != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied

        date = None
        form = ChooseFromDateForm(self.request.GET)
        if form.is_valid():
            date = form.cleaned_data['from_date']
        if form is None:
            context['form'] = ChooseFromDateForm()
        else:
            context['form'] = form

        context['results'] = get_top_results_by_athlete(athletes=analysis_group.athletes.all(), date=date, user=analysis_group.creator)
        context['events'] = Event.objects.filter(type=Event.INDIVIDUAL, use_points_in_athlete_total=True).order_by('id')
        context['analysis_group'] = analysis_group
        context['special_result_groups'] = SpecialResultGroup.objects.all()
        context['world_records_women'] = get_world_records(Athlete.FEMALE)
        context['world_records_men'] = get_world_records(Athlete.MALE)
        return context


def get_world_records(gender):
    world_records = []
    for event in Event.objects.filter(use_points_in_athlete_total=True).all():
        world_records.append(IndividualResult.public_objects.filter(athlete__gender=gender, event=event).order_by('time').first())
    return world_records


class RelayAnalysis(TemplateView):
    template_name = "analysis/relay_analysis.html"

    def post(self, *args, **kwargs):
        analysis_group = AnalysisGroup.objects.get(pk=self.kwargs.get('pk'))

        if analysis_group.creator != self.request.user:
            return HttpResponse('Unauthorized', status=401)

        form = ChooseFromDateForm(self.request.POST)
        date = None
        if form.is_valid():
            date = form.cleaned_data['from_date']

        if analysis_group.athletes.count() <= 10 and not analysis_group.simulation_in_progress:
            analysis_group.simulation_date_from = date
            create_combinations(analysis_group)
            analysis_group.simulation_in_progress = True
            analysis_group.save()
            return redirect('relay-analysis', analysis_group.id)

    def get_context_data(self, **kwargs):
        context = super(RelayAnalysis, self).get_context_data(**kwargs)
        analysis_group = AnalysisGroup.objects.get(pk=self.kwargs.get('pk'))
        if not analysis_group.public and analysis_group.creator != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied

        context['form'] = ChooseFromDateForm(required=False)
        context['events'] = Event.objects.filter(type=Event.RELAY_COMPLETE).order_by('pk').all()
        context['analysis_group'] = analysis_group
        context['group_teams'] = analysis_group.get_group_teams_with_full_setup()
        groupteam_count = analysis_group.groupteam_set.count()
        if groupteam_count > 0:
            context['progress'] = context['group_teams'].count() / analysis_group.groupteam_set.count() * 100
        context['progress'] = 0
        return context


def create_combinations(analysis_group):
    analysis_group.delete_all_previous_analysis()
    athletes = analysis_group.athletes.all()
    possible_teams = itertools.combinations(athletes, 6)

    group_teams = map(functools.partial(create_group_teams, analysis_group), possible_teams)
    group_teams = list(group_teams)
    last_group_team = group_teams[-1]
    first_group_team = next(iter(group_teams or []), None)

    params = {'current_group_team': first_group_team.id, 'last_group_team': last_group_team.id,
              'analysis_group': analysis_group.id}

    current_site = Site.objects.get_current()
    url = current_site.domain + str(reverse_lazy('create-setups'))

    p = Process(target=async_request, args=(url, params))
    p.daemon = True
    p.start()


def create_fastest_setups(request):
    if 'current_group_team' not in request.GET or 'last_group_team' not in request.GET or 'analysis_group' not in request.GET:
        return HttpResponseBadRequest
    analysis_group = AnalysisGroup.objects.get(pk=request.GET['analysis_group'])
    if not GroupTeam.objects.filter(pk=request.GET['current_group_team']).exists():
        analysis_group.simulation_in_progress = False
        analysis_group.save()
        analysis_group.clean_teams()
        return HttpResponseBadRequest

    last_group_team = GroupTeam.objects.get(pk=request.GET['last_group_team'])
    current_group_team = GroupTeam.objects.get(pk=request.GET['current_group_team'])
    events = Event.objects.filter(type=Event.RELAY_COMPLETE)
    for event in events:
        get_fastest_time_for_team_and_event(current_group_team, event, analysis_group)

    if last_group_team.id is not current_group_team.id:
        params = {'current_group_team': current_group_team.id + 1, 'last_group_team': last_group_team.id,
                  'analysis_group': analysis_group.id}

        current_site = Site.objects.get_current()
        url = current_site.domain + str(reverse_lazy('create-setups'))

        p = Process(target=async_request, args=(url, params))
        p.daemon = True
        p.start()
        sleep(1)
    else:
        analysis_group.clean_teams()
        analysis_group.simulation_in_progress = False
        analysis_group.save()

    return HttpResponse()


def async_request(url, params):
    session = requests.Session()
    session.get(url, params=params)


def get_time_for_setup(setup, event, analysis_group):
    index = 0
    time_for_current_setup = timedelta(0)
    for athlete in setup:
        time = get_time_by_event_athlete_and_index(event, athlete, index, analysis_group)
        if time:
            time_for_current_setup += time
        else:
            return False
        index += 1
    return time_for_current_setup


def get_time_by_event_athlete_and_index(event, athlete, index, analysis_group):
    relay_order = RelayOrder.objects.filter(event=event, index=index).first()
    segment = relay_order.segment
    individual_result = IndividualResult.find_fastest_by_athlete_and_event(athlete, segment, analysis_group)
    if individual_result:
        return individual_result.time
    return False


def create_group_teams(group, possible_team):
    group_team = GroupTeam()
    group_team.analysis_group = group
    group_team.save()
    for athlete in possible_team:
        group_team.athletes.add(athlete)
    group_team.save()
    return group_team


def get_fastest_time_for_team_and_event(group_team, event, analysis_group):
    fastest = None
    athletes = group_team.athletes.all()

    if event.are_segments_same():
        relay_order = RelayOrder.objects.filter(event=event).first()
        segment = relay_order.segment
        qs = IndividualResult.objects.filter(
            Q(extra_analysis_time_by=analysis_group.creator) | Q(extra_analysis_time_by=None))
        results = qs.filter(event=segment, athlete__in=athletes).values('athlete') \
                      .annotate(pb=Min('time')).order_by('pb').all()[:4]
        if len(list(results)) < 4:
            return
        current_setup = []
        total_time = timedelta(0)
        for result in results:
            current_setup.append(result['athlete'])
            total_time += result['pb']
        fastest = {'setup': current_setup, 'time': total_time}
    else:
        for ordered_setup in itertools.combinations(athletes, 4):
            for setup in itertools.permutations(ordered_setup):
                time_for_current_setup = get_time_for_setup(setup, event, analysis_group)
                if time_for_current_setup and (fastest is None or fastest["time"] > time_for_current_setup):
                    fastest = {'setup': setup, 'time': time_for_current_setup}
    if fastest is None:
        return
    fastest_setup = GroupEventSetup()
    fastest_setup.event = event
    fastest_setup.time = fastest['time']
    fastest_setup.save()
    index = 0
    for athlete in fastest['setup']:
        if type(athlete) is not Athlete:
            athlete = Athlete.objects.get(pk=athlete)
        segment = GroupEvenSetupSegment.objects.create(
            athlete=athlete,
            index=index,
            group_event_setup=fastest_setup
        )
        segment.save()
        index += 1
    fastest_setup.save()
    group_team.setups.add(fastest_setup)
    group_team.save()
