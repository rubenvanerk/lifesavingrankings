import operator
import random

from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.mail import send_mail
from django.db.models import Count, Min
from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView
from .models import *
from django.http import Http404, HttpResponseRedirect, HttpResponse
from .forms import *


class FrontPageRecords(TemplateView):

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['athlete_count'] = Athlete.objects.all().count()
        context['result_count'] = IndividualResult.objects.all().count()
        context['home'] = True
        context['last_added_competition'] = Competition.objects.filter(slug__isnull=False).filter(
            is_concept=False).order_by('-date').first()

        top_results = {'genders': {'women': [], 'men': []}}
        for gender in top_results['genders']:
            for event in Event.objects.filter(type=1).all():
                top_result = next(
                    iter(event.get_top_by_competition_and_gender(competition=None, gender=gender, limit=1)), None)
                top_results['genders'][gender].append(top_result)

        context['top_results'] = top_results

        return context

    template_name = 'rankings/front_page_records.html'


class CompetitionOverview(TemplateView):
    template_name = 'rankings/competition_overview.html'

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise Http404
        competition_slug = self.kwargs.get('competition_slug')
        competition = Competition.objects.filter(slug=competition_slug).first()
        nationality = Nationality.objects.get(pk=request.POST['country'])

        for athlete in competition.get_athletes():
            if not athlete.nationality:
                athlete.nationality = nationality
                athlete.save()

        return HttpResponseRedirect(reverse('competition-overview', args=[competition.slug]))

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
            context['events'][event.name]['men'] = event.get_top_by_competition_and_gender(competition=competition,
                                                                                           gender=1, limit=limit)
            context['events'][event.name]['women'] = event.get_top_by_competition_and_gender(competition=competition,
                                                                                             gender=2, limit=limit)
        context['competition'] = competition
        context['nationalities'] = Nationality.objects.all()
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()

        competition = context['competition']
        if 'publish' in self.request.GET and self.request.GET['publish'] == 'true' and self.request.user.is_superuser:
            competition.is_concept = False
            competition.save()
            for result in competition.individualresult_set.all():
                result.calculate_points()
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
                                                          extra_analysis_time_by=None).order_by('athlete',
                                                                                                'time').distinct(
                'athlete')
            results_men = IndividualResult.objects.filter(id__in=results_men).order_by('time')[:limit]
            context['events'][event.name]['men'] = results_men

            results_women = IndividualResult.objects.filter(event=event, athlete__gender=2,
                                                            extra_analysis_time_by=None).distinct('athlete')
            results_women = sorted(results_women, key=operator.attrgetter('time'))[:limit]
            context['events'][event.name]['women'] = results_women
        return context


class PersonalBests(TemplateView):
    athlete = None

    def get_athlete(self):
        if self.athlete is not Athlete:
            slug = self.kwargs.get('slug')
            self.athlete = Athlete.objects.filter(slug=slug).first()
            if not self.athlete:
                raise Http404
        return self.athlete

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        nationality = Nationality.objects.get(pk=request.POST['country'])
        athlete = self.get_athlete()
        athlete.nationality = nationality
        athlete.save()
        context['athlete'] = athlete
        return super(TemplateView, self).render_to_response(context)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        athlete = self.get_athlete()

        context['personal_bests'] = {}

        qs = IndividualResult.find_by_athlete(athlete) \
            .filter(event__type=1, extra_analysis_time_by=None) \
            .order_by('event', 'time').distinct('event')
        context['personal_bests']['individual'] = IndividualResult.objects.filter(id__in=qs).order_by('time')

        qs = IndividualResult.find_by_athlete(athlete) \
            .filter(event__type=2, extra_analysis_time_by=None) \
            .order_by('event', 'time').distinct('event')
        context['personal_bests']['relay'] = IndividualResult.objects.filter(id__in=qs).order_by('time')

        context['athlete'] = athlete
        context['nationalities'] = Nationality.objects.all()
        return context

    template_name = 'rankings/personal_best.html'


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

        qs = qs.filter(athlete=athlete, event=event)
        if self.request.user.is_authenticated:
            user = self.request.user
            qs = qs.filter(Q(extra_analysis_time_by=user) | Q(extra_analysis_time_by=None))
        else:
            qs = qs.filter(extra_analysis_time_by=None)
        qs = qs.order_by('time')
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['athlete'] = self.get_athlete()
        context['event'] = self.get_event()
        return context

    template_name = 'rankings/event_by_athlete.html'


@login_required
def add_result(request, athlete_slug):
    athlete = Athlete.objects.filter(slug=athlete_slug).first()
    if athlete is None:
        raise Http404

    if request.method == 'POST':
        form = AddResultForm(request.POST)

        if form.is_valid():
            time = form['time'].value()
            date = form['date'].value()
            event_id = form['event'].value()
            event = Event.objects.get(pk=event_id)

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

            return HttpResponseRedirect(reverse('athlete-event', args=(athlete_slug, event.generate_slug())))
        else:
            return render(request, 'rankings/add_result.html', {'form': form, 'athlete': athlete})
    else:
        form = AddResultForm

        return render(request, 'rankings/add_result.html', {'form': form, 'athlete': athlete})


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

            return render(request, 'rankings/request_competition.html', {'form': form, 'form_sent': True})
        else:
            return render(request, 'rankings/request_competition.html', {'form': form})
    else:
        form = RequestCompetitionForm

        return render(request, 'rankings/request_competition.html', {'form': form})


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
        gender = gender_name_to_int(self.kwargs.get('gender'))

        qs = qs.filter(event=event.id, athlete__gender=gender).values('athlete').annotate(pb=Min('time')).order_by(
            'time')

        qs = qs.values('athlete_id',
                       'athlete__name',
                       'athlete__year_of_birth',
                       'time',
                       'competition__date',
                       'competition__name',
                       'competition__slug',
                       'event__name',
                       'athlete__slug',
                       'points',
                       'athlete__nationality__flag_code',
                       'athlete__nationality__name')

        best_result_per_athlete = {}
        for result in qs:
            best_result_per_athlete.setdefault(result['athlete_id'], result)

        return best_result_per_athlete

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['event'] = self.get_event()
        context['gender'] = self.kwargs.get('gender')
        return context

    template_name = 'rankings/best_by_event.html'


class Search(ListView):
    model = Athlete

    def get_context_data(self, **kwargs):
        context = super(Search, self).get_context_data(**kwargs)

        athletes = super(Search, self).get_queryset()

        query = self.request.GET.get('athlete').strip()

        if not query:
            context['search_results'] = {}
            context['query'] = query
            return context

        parts = query.split(' ')

        if query and len(parts) > 1:
            for part in parts:
                athletes = athletes.filter(name__unaccent__icontains=part)
        else:
            athletes = athletes.filter(name__unaccent__icontains=query)

        athletes.order_by('name', 'first_name', 'last_name')

        context['search_results'] = athletes
        context['query'] = query
        return context

    template_name = 'rankings/search.html'


class DeleteEmptyAthletes(ListView):
    model = Athlete
    template_name = 'rankings/list_empty_athletes.html'

    def get_context_data(self, **kwargs):
        context = super(DeleteEmptyAthletes, self).get_context_data(**kwargs)

        athletes = Athlete.objects.annotate(
            result_count=Count('individualresult')
        ).filter(result_count=0)

        context['athletes'] = athletes
        return context


@user_passes_test(lambda u: u.is_staff)
def label_nationality(request, pk):
    athlete = Athlete.objects.filter(pk=pk).first()
    queue = Athlete.objects.filter(nationality=None).annotate(num_results=Count('individualresult')).filter(
        num_results__gt=12).all()
    next_athlete = random.choice(queue)
    if not athlete:
        return HttpResponseRedirect(reverse('label_athlete', kwargs={'pk': next_athlete.pk}))

    if request.method == 'POST':
        nationality = Nationality.objects.get(pk=request.POST['country'])
        athlete.nationality = nationality
        athlete.save()
        return HttpResponseRedirect(reverse('label_athlete', kwargs={'pk': next_athlete.pk}))

    athlete_count = Athlete.objects.count()
    labeled_athletes = Athlete.objects.filter(~Q(nationality=None)).count()
    progress = labeled_athletes / athlete_count * 100

    return render(request, 'rankings/label_nationality.html',
                  {'athlete': athlete, 'nationalities': Nationality.objects.all(), 'athlete_count': athlete_count,
                   'labeled_athletes': labeled_athletes, 'progress': progress, 'next_athlete': next_athlete, 'queue': queue})


@user_passes_test(lambda u: u.is_superuser)
def delete_empty_athletes(request):
    athletes = Athlete.objects.annotate(
        result_count=Count('individualresult')
    ).filter(result_count=0)

    deleted_count = str(len(athletes))

    athletes.delete()

    return HttpResponse(deleted_count + ' athletes deleted')


@user_passes_test(lambda u: u.is_superuser)
def calculate_points(request):
    for result in IndividualResult.objects.filter(event__type=1, points=0):
        result.calculate_points()

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
