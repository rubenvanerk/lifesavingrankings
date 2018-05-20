import functools
import itertools
from datetime import timedelta
from multiprocessing import Process
from time import sleep

import requests

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Min
from django import forms
from django.http import HttpResponse, HttpResponseBadRequest
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView, CreateView

from analysis.forms import ChooseFromDateForm
from analysis.models import SpecialResult, AnalysisGroup, GroupTeam, GroupEventSetup
from rankings.models import Event, Athlete, IndividualResult, RelayOrder


class GroupAnalysis(TemplateView):
    template_name = 'analysis/analysis.html'

    def get_context_data(self, **kwargs):
        context = super(GroupAnalysis, self).get_context_data(**kwargs)
        group_id = self.kwargs.get('group_id')
        group = AnalysisGroup.objects.get(pk=group_id)
        if not group.public and group.creator != self.request.user:
            raise PermissionDenied

        date = None
        form = ChooseFromDateForm(self.request.GET)
        if form.is_valid():
            date = form['from_date'].value()
        if form is None:
            context['form'] = ChooseFromDateForm()
        else:
            context['form'] = form

        context['results'] = get_top_results_by_athlete(athletes=group.athlete.all(), date=date)
        context['special_results'] = SpecialResult.objects.filter(gender=group.gender).order_by('event_id')
        context['events'] = Event.objects.all().order_by('id')
        return context


def get_top_results_by_athlete(gender=None, athletes=None, date=None):
    events = Event.objects.all().order_by('id')
    if athletes is None:
        athletes = Athlete.objects.filter(gender=gender)
    results = {}

    for athlete in athletes:
        individual_results = []
        for event in events:
            qs = IndividualResult.find_by_athlete_and_event(athlete, event)
            if date is not None:
                qs = qs.filter(competition__date__gte=date)
            qs = qs.values('event__name',
                           'event_id')
            qs = qs.annotate(pb=Min('time'))
            individual_results.append(qs)
        results[athlete.id] = individual_results
    return results


class AnalysisGroupListView(LoginRequiredMixin, ListView):
    model = AnalysisGroup

    def get_queryset(self):
        user = self.request.user
        qs = super(AnalysisGroupListView, self).get_queryset()
        qs = qs.filter(creator=user).order_by('id')
        return qs


class PublicAnalysisGroupListView(ListView):
    model = AnalysisGroup

    def get_queryset(self):
        qs = super(PublicAnalysisGroupListView, self).get_queryset()
        qs = qs.filter(public=True)
        return qs

    def get_context_data(self, **kwargs):
        context = super(PublicAnalysisGroupListView, self).get_context_data()
        context['public'] = True
        return context


class AnalysisGroupForm(forms.ModelForm):
    class Meta:
        model = AnalysisGroup
        fields = ['name', 'athlete', 'public', 'gender']
        widgets = {
            'athlete': forms.CheckboxSelectMultiple
        }


class AnalysisGroupUpdate(LoginRequiredMixin, UpdateView):
    model = AnalysisGroup
    form_class = AnalysisGroupForm
    success_url = reverse_lazy('analysis:private-group-list')

    def get_object(self, queryset=None):
        obj = super(AnalysisGroupUpdate, self).get_object()
        if obj.creator != self.request.user:
            raise PermissionDenied
        else:
            return obj


class AnalysisGroupCreate(LoginRequiredMixin, CreateView):
    model = AnalysisGroup
    form_class = AnalysisGroupForm
    success_url = reverse_lazy('analysis:private-group-list')

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super(AnalysisGroupCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(AnalysisGroupCreate, self).get_context_data()
        context['new_group'] = True
        return context


class TeamMaker(TemplateView):
    template_name = "analysis/team_maker.html"

    def get_context_data(self, **kwargs):
        context = super(TeamMaker, self).get_context_data(**kwargs)
        group_id = self.kwargs.get('group_id')
        analysis_group = AnalysisGroup.objects.get(pk=group_id)
        if not analysis_group.public and analysis_group.creator != self.request.user:
            raise PermissionDenied
        if 'recalculate' in self.request.GET and self.request.GET['recalculate'] is '1':
            create_combinations(analysis_group)
        context['events'] = Event.objects.filter(type=3).order_by('pk').all()
        context['analysis_group'] = analysis_group
        context['group_teams'] = analysis_group.get_group_teams_with_full_setup()
        return context


def create_combinations(analysis_group):
    analysis_group.delete_all_previous_analysis()
    athletes = analysis_group.athlete.all()
    possible_teams = itertools.combinations(athletes, 6)

    group_teams = map(functools.partial(create_group_teams, analysis_group), possible_teams)
    group_teams = list(group_teams)
    last_group_team = group_teams[-1]
    first_group_team = next(iter(group_teams or []), None)

    params = {'current_group_team': first_group_team.id, 'last_group_team': last_group_team.id}
    url = 'https://www.lifesavingrankings.nl/analysis/analyse/create-fastest-setups/'
    p = Process(target=async_request, args=(url, params))
    p.daemon = True
    p.start()


def create_fastest_setups(request):
    if 'current_group_team' not in request.GET or 'last_group_team' not in request.GET:
        return HttpResponseBadRequest
    last_group_team = GroupTeam.objects.get(pk=request.GET['last_group_team'])
    current_group_team = GroupTeam.objects.get(pk=request.GET['current_group_team'])
    events = Event.objects.filter(type=3)
    for event in events:
        get_fastest_time_for_team_and_event(current_group_team, event)

    if last_group_team.id is not current_group_team.id:
        params = {'current_group_team': current_group_team.id + 1, 'last_group_team': last_group_team.id}
        url = 'https://www.lifesavingrankings.nl/analysis/analyse/create-fastest-setups/'
        p = Process(target=async_request, args=(url, params))
        p.daemon = True
        p.start()
        sleep(1)

    return HttpResponse()


def get_fastest_setup(event, group_team):
    params = {'event': event.id, 'group_team': group_team.id}
    url = 'https://www.lifesavingrankings.nl/analysis/analyse/fastest-by-group-event/'
    p = Process(target=async_request, args=(url, params))
    p.daemon = True
    p.start()


def async_request(url, params):
    session = requests.Session()
    session.get(url, params=params)


def get_time_for_setup(setup, event):
    index = 0
    time_for_current_setup = timedelta(0)
    for athlete in setup:
        time = get_time_by_event_athlete_and_index(event, athlete, index)
        if time:
            time_for_current_setup += time
        else:
            return False
        index += 1
    return time_for_current_setup


def get_time_by_event_athlete_and_index(event, athlete, index):
    relay_order = RelayOrder.objects.filter(event=event, index=index).first()
    segment = relay_order.segment
    individual_result = IndividualResult.find_fastest_by_athlete_and_event(athlete, segment)
    if individual_result:
        return individual_result.time
    return False


def create_possible_teams(request):
    if 'analysis_group' not in request.GET:
        return HttpResponseBadRequest()
    analysis_group = AnalysisGroup.objects.get(pk=request.GET['analysis_group'])

    athletes = analysis_group.athlete.all()
    possible_teams = itertools.combinations(athletes, 6)

    for team in possible_teams:
        group_team = GroupTeam(analysis_group=analysis_group)
        for athlete in team:
            group_team.athletes.add(athlete)

    return HttpResponse()


def create_group_teams(group, possible_team):
    group_team = GroupTeam()
    group_team.analysis_group = group
    group_team.save()
    for athlete in possible_team:
        group_team.athletes.add(athlete)
    group_team.save()
    return group_team


def get_fastest_time_for_team_and_event(group_team, event):
    # if 'group_team' not in request.GET or 'event' not in request.GET:
    #     return HttpResponseBadRequest

    # group_team = GroupTeam.objects.get(pk=request.GET['group_team'])
    # event = Event.objects.get(pk=request.GET['event'])

    fastest = None
    athletes = group_team.athletes.all()

    if event.are_segments_same():
        relay_order = RelayOrder.objects.filter(event=event).first()
        segment = relay_order.segment
        results = IndividualResult.objects.filter(event=segment, athlete__in=athletes).values('athlete')\
            .annotate(pb=Min('time')).order_by('pb').all()[:4]
        current_setup = []
        total_time = timedelta(0)
        for result in results:
            current_setup.append(result['athlete'])
            total_time += result['pb']
        fastest = {'setup': current_setup, 'time': total_time}
    else:
        for ordered_setup in itertools.combinations(athletes, 4):
            for setup in itertools.permutations(ordered_setup):
                time_for_current_setup = get_time_for_setup(setup, event)
                if time_for_current_setup and (fastest is None or fastest["time"] > time_for_current_setup):
                    fastest = {'setup': setup, 'time': time_for_current_setup}
    if fastest is None:
        return
    fastest_setup = GroupEventSetup()
    fastest_setup.event = event
    fastest_setup.time = fastest['time']
    fastest_setup.save()
    for athlete in fastest['setup']:
        fastest_setup.athletes.add(athlete)
    fastest_setup.save()
    group_team.setups.add(fastest_setup)
    group_team.save()
    # return HttpResponse()
