from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^athlete/(?P<athlete_id>[0-9]+)/(?P<event_id>[a-z0-9]+)$',
        view=views.EventByAthlete.as_view(),
        name='athlete-event'
    ),
    url(
        regex=r'^athlete/(?P<athlete_id>[0-9]+)',
        view=views.PersonalBests.as_view(),
        name='athlete-overview'
    ),
    url(
        regex=r'^top/(?P<event_id>[0-9]+)/(?P<gender>\bmen\b|\bwomen\b)',
        view=views.BestByEvent.as_view(),
        name='best-by-event'
    ),
]
