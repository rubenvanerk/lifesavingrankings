from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from rankings.views import athlete_redirect_athlete_id_to_slug, athlete_redirect_event_id_to_slug, \
    redirect_event_id_to_slug
from . import views

urlpatterns = [
    url(
        regex=r'^athlete/(?P<slug>[a-z0-9\-]+)/(?P<event_id>[0-9]+)$',
        view=athlete_redirect_event_id_to_slug,
        name='athlete-event-redirect'
    ),
    url(
        regex=r'^athlete/(?P<slug>[a-z0-9\-]+)/(?P<event_name>[a-z0-9\-()]+)$',
        view=views.EventByAthlete.as_view(),
        name='athlete-event'
    ),
    url(
        regex=r'^athlete/(?P<athlete_id>[0-9]+)',
        view=athlete_redirect_athlete_id_to_slug,
        name='athlete-redirect'
    ),
    url(
        regex=r'^athlete/(?P<slug>[a-z0-9\-]+)',
        view=views.PersonalBests.as_view(),
        name='athlete-overview'
    ),
    url(
        regex=r'^top/(?P<event_id>[0-9]+)/(?P<gender>\bmen\b|\bwomen\b)',
        view=redirect_event_id_to_slug,
        name='best-by-event-redirect'
    ),
    url(
        regex=r'^top/(?P<event_name>[a-z0-9\-()]+)/(?P<gender>\bmen\b|\bwomen\b)',
        view=views.BestByEvent.as_view(),
        name='best-by-event'
    ),
    url(
        regex=r'^merge-athletes',
        view=views.merge_athletes,
        name='merge-athletes'
    ),
    url(
        regex=r'^search',
        view=views.Search.as_view(),
        name='search'
    ),
]
