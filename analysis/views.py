from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Min
from django import forms
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView, CreateView

from analysis.models import SpecialResult, AnalysisGroup
from rankings.models import Event, Athlete, IndividualResult


class GroupAnalysis(TemplateView):
    template_name = 'analysis/analysis.html'

    def get_context_data(self, **kwargs):
        context = super(GroupAnalysis, self).get_context_data(**kwargs)
        group_id = self.kwargs.get('group_id')
        group = AnalysisGroup.objects.get(pk=group_id)
        if not group.public and group.creator != self.request.user:
            raise PermissionDenied
        context['results'] = get_top_results_by_athlete(athletes=group.athlete.all())
        context['special_results'] = SpecialResult.objects.filter(gender=group.gender)
        context['events'] = Event.objects.all()
        return context


def get_top_results_by_athlete(gender=None, athletes=None):
    events = Event.objects.all()
    if athletes is None:
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


