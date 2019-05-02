from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from django.urls import path

from rankings.views import athlete_redirect_athlete_id_to_slug, athlete_redirect_event_id_to_slug, \
    redirect_event_id_to_slug, add_result, report_duplicate, request_competition
from . import views

urlpatterns = [
    url(
        regex=r'^athlete/(?P<slug>[a-z0-9\-]+)/(?P<event_id>[0-9]+)$',
        view=athlete_redirect_event_id_to_slug,
        name='athlete-event-redirect'
    ),
    url(
        regex=r'^athlete/add-time/(?P<athlete_slug>[a-z0-9\-]+)/',
        view=add_result,
        name='athlete-add-time'
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
        regex=r'^events',
        view=views.EventOverview.as_view(),
        name='event-overview'
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
        regex=r'^list-empty-athletes',
        view=views.DeleteEmptyAthletes.as_view(),
        name='list-empty-athletes'
    ),
    url(
        regex=r'^delete-empty-athletes',
        view=views.delete_empty_athletes,
        name='delete-empty-athletes'
    ),
    url(
        regex=r'^calculate-points',
        view=views.calculate_points,
        name='calculate_points'
    ),
    url(
        regex=r'^label-athlete/(?P<pk>[0-9]+)$',
        view=views.label_nationality,
        name='label_athlete'
    ),
    url(
        regex=r'^search',
        view=views.Search.as_view(),
        name='search'
    ),
    url(
        regex=r'^competitions/request',
        view=request_competition,
        name='request-competition'
    ),
    url(
        regex=r'^competitions',
        view=views.CompetitionListView.as_view(),
        name='competition-list'
    ),
    url(
        regex=r'^competition/(?P<competition_slug>[a-z0-9\-]+)/(?P<event_name>[a-z0-9\-()]+)/(?P<gender>\bmen\b|\bwomen\b)',
        view=views.CompetitionEvent.as_view(),
        name='competition-event'
    ),
    url(
        regex=r'^competition/(?P<competition_slug>[a-z0-9\-]+)',
        view=views.CompetitionOverview.as_view(),
        name='competition-overview'
    ),
    url(
        regex=r'^report-duplicate',
        view=report_duplicate
    ),
    url(
        regex=r'^merge-request/list/',
        view=views.MergeRequestListView.as_view(),
        name='merge-request-list'
    ),
    path('merge-request/delete/<pk>', views.MergeRequestDeleteView.as_view(), name='merge-request-delete'),
    path('merge-request/delete/<pk>', views.MergeRequestDeleteView.as_view(), name='merge-request-delete'),
    path('merge-request/detail/<pk>', views.MergeRequestDetailView.as_view(), name='merge-request-detail'),
]
