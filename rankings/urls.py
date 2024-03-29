from __future__ import absolute_import, unicode_literals

from django.urls import path, register_converter
from . import views, converters

register_converter(converters.GenderConverter, 'gender')

urlpatterns = [
    # legacy redirects
    path('athlete/<int:athlete_id>/', views.athlete_redirect_athlete_id_to_slug),
    path('athlete/<slug:athlete_slug>/<int:event_id>/', views.athlete_redirect_event_id_to_slug),
    path('top/<int:event_id>/<gender:gender>/', views.redirect_event_id_to_slug),

    # athlete routes
    path('athlete/<slug:athlete_slug>/', views.AthleteDetail.as_view(), name='athlete-detail'),
    path('athlete/<slug:athlete_slug>/timeline/', views.AthleteTimeline.as_view(), name='athlete-timeline'),
    path('athlete/add-time/<slug:athlete_slug>/', views.add_result, name='athlete-add-time'),
    path('individual-result/<int:pk>/delete/', views.IndividualResultDelete.as_view(), name='delete-time'),
    path('athlete/<slug:athlete_slug>/<slug:event_slug>/', views.AthleteEvent.as_view(), name='athlete-event'),
    path('search/', views.Search.as_view(), name='search'),
    path('athletes/<str:query>/', views.api_search_athletes),

    # event routes
    path('events/', views.EventList.as_view(), name='event-list'),
    path('top/<slug:event_slug>/<gender:gender>/', views.EventAthletes.as_view(), name='best-by-event'),

    # competitions
    path('competition/request/', views.request_competition, name='request-competition'),
    path('competition/<slug:competition_slug>/', views.CompetitionDetail.as_view(), name='competition-detail'),
    path('competitions/', views.CompetitionListView.as_view(), name='competition-list'),
    path('competition/<slug:competition_slug>/<slug:event_slug>/<gender:gender>/', views.CompetitionEvent.as_view(),
         name='competition-event'),

    # team routes
    path('teams/', views.TeamListView.as_view(), name='team-list'),
    path('teams/<slug:slug>/', views.TeamDetailView.as_view(), name='team-detail'),
    path('teams/<slug:team_slug>/<slug:competition_slug>/', views.TeamCompetitionView.as_view(), name='team-competition'),

    # utilities
    path('recalculate-points/', views.recalculate_points),
    path('label-athlete/<int:pk>/', views.label_nationality, name='label-athlete'),
    path('report-duplicate/', views.report_duplicate),
    path('merge-requests-list', views.MergeRequestListView.as_view(), name='merge-request-list'),
    path('merge-request/delete/<pk>', views.MergeRequestDeleteView.as_view(), name='merge-request-delete'),
    path('merge-request/detail/<pk>', views.MergeRequestDetailView.as_view(), name='merge-request-detail'),
]
