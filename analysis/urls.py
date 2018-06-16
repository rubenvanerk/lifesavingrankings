from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^group/(?P<group_id>[0-9]+)/relay-analysis/',
        view=views.RelayAnalysis.as_view(),
        name='relay-analysis'
    ),
    url(
        regex=r'^group/(?P<pk>[0-9]+)/edit',
        view=views.AnalysisGroupUpdate.as_view(),
        name='group-edit'
    ),
    url(
        regex=r'^group/(?P<group_id>[0-9]+)/individual-analysis/',
        view=views.IndividualAnalysis.as_view(),
        name='individual-analysis'
    ),
    url(
        regex=r'^group/create/',
        view=views.AnalysisGroupCreate.as_view(),
        name='group-create'
    ),
    url(
        regex=r'^my-groups/',
        view=views.AnalysisGroupListView.as_view(),
        name='private-group-list'
    ),
    url(
        regex=r'^public-groups/',
        view=views.PublicAnalysisGroupListView.as_view(),
        name='public-group-list'
    ),
    url(
        regex=r'^analyse/create-fastest-setups/',
        view=views.create_fastest_setups,
        name='create-setups'
    )
]
