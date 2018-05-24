from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from django.urls import path

from rankings.views import athlete_redirect_id_to_slug
from . import views

urlpatterns = [
    url(
        regex=r'^athlete/(?P<slug>[a-z0-9\-]+)/(?P<event_name>[a-z0-9\-()]+)$',
        view=views.EventByAthlete.as_view(),
        name='athlete-event'
    ),
    url(
        regex=r'^athlete/(?P<athlete_id>[0-9]+)',
        view=athlete_redirect_id_to_slug,
        name='athlete-redirect'
    ),
    url(
        regex=r'^athlete/(?P<slug>[a-z0-9\-]+)',
        view=views.PersonalBests.as_view(),
        name='athlete-overview'
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
