import itertools
from datetime import timedelta

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Min
from django import forms
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView, CreateView

from analysis.forms import ChooseFromDateForm
from analysis.models import SpecialResult, AnalysisGroup
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
        group = AnalysisGroup.objects.get(pk=group_id)
        if not group.public and group.creator != self.request.user:
            raise PermissionDenied
        context["combinations"] = get_combinations(group)
        return context


def get_combinations(group):
    athletes = group.athlete.all()
    possible_teams = itertools.combinations(athletes, 6)
    events = Event.objects.filter(type=3)
    combinations = {}
    team_index = 0
    event_index = 0
    for team in possible_teams:
        total_time = timedelta(0)
        combinations["team" + str(team_index)] = {}
        combinations["team" + str(team_index)]["athletes"] = team
        combinations["team" + str(team_index)]["times"] = {}
        missing_setup = False
        for event in events:
            fastest_setup = get_fastest_setup(team, event)
            combinations["team" + str(team_index)]["times"][event.name] = fastest_setup
            if fastest_setup:
                total_time += fastest_setup["time"]
            else:
                missing_setup = True
                combinations.pop("team" + str(team_index))
                break
            event_index += 1
        if not missing_setup:
            combinations["team" + str(team_index)]["total_time"] = total_time
            team_index += 1
        event_index = 0
    return combinations


def get_fastest_setup(team, event):
    """

    :param team:
    :type event: Event
    """
    fastest = None
    for ordered_setup in itertools.combinations(team, 4):
        if event.are_segments_same():
            time_for_current_setup = get_time_for_setup(ordered_setup, event)
            current_setup = ordered_setup
            if time_for_current_setup and (fastest is None or fastest["time"] > time_for_current_setup):
                fastest = {'setup': current_setup, 'time': time_for_current_setup}
        else:
            for setup in itertools.permutations(ordered_setup):
                current_setup = setup
                time_for_current_setup = get_time_for_setup(setup, event)
                if time_for_current_setup and (fastest is None or fastest["time"] > time_for_current_setup):
                    fastest = {'setup': current_setup, 'time': time_for_current_setup}
    return fastest


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
