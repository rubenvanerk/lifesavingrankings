from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from rankings.models import Athlete, IndividualResult, Competition, Event
from rankings.views import gender_name_to_int


class Home(TemplateView):

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['athlete_count'] = Athlete.objects.all().count()
        context['result_count'] = IndividualResult.public_objects.all().count()

        public_competition_count = (Competition.public_objects
                                    .filter(status=Competition.IMPORTED)
                                    .exclude(slug__isnull=True)
                                    .exclude(slug='')
                                    .count())
        context['competition_count'] = public_competition_count
        context['home'] = True

        last_published_competitions = (Competition.public_objects
                                       .filter(slug__isnull=False, status=2, published_on__isnull=False)
                                       .order_by('-published_on'))
        context['last_published_competitions'] = last_published_competitions[:5]

        top_results = {'genders': {'women': [], 'men': []}}
        events = Event.objects.filter(type=Event.INDIVIDUAL).all();
        for gender in top_results['genders']:
            gender_int = gender_name_to_int(gender)
            for event in events:
                top_result = IndividualResult.public_objects.filter(event=event, athlete__gender=gender_int).order_by(
                    'time').select_related('competition', 'athlete', 'event').first()
                if top_result:
                    top_results['genders'][gender].append(top_result)

        context['top_results'] = top_results

        return context

    template_name = 'home.html'


class Account(LoginRequiredMixin, TemplateView):
    athlete = None
    template_name = 'account.html'


def error_404_view(request, exception):
    data = {"message": "Error 404: Page not found"}
    return render(request, '404.html', data)


def error_500_view(request):
    data = {"message": "Error 500: Server error"}
    return render(request, '500.html', data)


def ultimate_lifesaver(request):
    return render(request, 'ultimate-lifesaver.html')


def changelog(request):
    return render(request, 'changelog.html', {'static': True})


def about(request):
    return render(request, 'about.html', {'static': True})


def rankings_redirect(request, path):
    return redirect(path)
