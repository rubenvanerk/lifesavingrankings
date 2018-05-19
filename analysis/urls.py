from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    # url(
    #     regex=r'(?P<gender>\bmen\b|\bwomen\b)',
    #     view=views.Analysis.as_view(),
    #     name='analysis'
    # ),
    url(
        regex=r'^group/(?P<group_id>[0-9]+)/team-maker/',
        view=views.TeamMaker.as_view(),
        name='team-maker'
    ),
    url(
        regex=r'^group/(?P<pk>[0-9]+)/edit',
        view=views.AnalysisGroupUpdate.as_view(),
        name='group-edit'
    ),
    url(
        regex=r'^group/(?P<group_id>[0-9]+)/',
        view=views.GroupAnalysis.as_view(),
        name='group-analysis'
    ),
    url(
        regex=r'^group/create',
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
    )
]
