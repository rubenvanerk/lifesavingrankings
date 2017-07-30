from django.db.models import Min
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView, CreateView

from analysis.models import SpecialResult, AnalysisGroup
from rankings.models import Event, Athlete, IndividualResult
from rankings.views import gender_name_to_int


class Analysis(TemplateView):
    template_name = 'analysis/analysis.html'

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


class AnalysisGroupListView(ListView):

    model = AnalysisGroup

    def get_queryset(self):
        user = self.request.user
        qs = super(AnalysisGroupListView, self).get_queryset()
        qs.filter(creator=user)
        return qs

    def get_context_data(self, **kwargs):
        context = super(AnalysisGroupListView, self).get_context_data(**kwargs)
        context['extra'] = 'extra'

        return context


class AnalysisGroupUpdate(UpdateView):

    model = AnalysisGroup
    fields = ['name', 'athlete', 'public']
    success_url = reverse_lazy('analysis:group-list')


class AnalysisGroupCreate(CreateView):

    model = AnalysisGroup
    fields = ['name', 'athlete', 'public']
    success_url = reverse_lazy('analysis:group-list')

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super(AnalysisGroupCreate, self).form_valid(form)
