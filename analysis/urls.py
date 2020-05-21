from __future__ import absolute_import, unicode_literals

from django.urls import path

from . import views

urlpatterns = [
    path('public-groups/', views.PublicAnalysisGroupListView.as_view(), name='public-group-list'),
    path('my-groups/', views.AnalysisGroupListView.as_view(), name='private-group-list'),
    path('group/create/', views.AnalysisGroupCreate.as_view(), name='group-create'),
    path('group/<int:pk>/edit/', views.AnalysisGroupUpdate.as_view(), name='group-edit'),
    path('group/<int:pk>/delete/', views.AnalysisGroupDelete.as_view(), name='group-delete'),
    path('group/<int:pk>/individual-analysis/', views.IndividualAnalysis.as_view(), name='individual-analysis'),
    path('group/<int:pk>/relay-analysis/', views.RelayAnalysis.as_view(), name='relay-analysis'),
    path('analyse/create-fastest-setups/', views.create_fastest_setups, name='create-setups')
]
