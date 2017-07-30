from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'(?P<gender>\bmen\b|\bwomen\b)',
        view=views.Analysis.as_view(),
        name='analysis'
    ),
    url(
        regex=r'^group/(?P<pk>[0-9]+)/edit',
        view=views.AnalysisGroupUpdate.as_view(),
        name='group-edit'
    ),
    url(
        regex=r'^group/(?P<group_id>[0-9]+)',
        view=views.GroupAnalysis.as_view(),
        name='group-analysis'
    ),
    url(
        regex=r'^groups/',
        view=views.AnalysisGroupListView.as_view(),
        name='group-list'
    ),
    url(
        regex=r'^group/create',
        view=views.AnalysisGroupCreate.as_view(),
        name='group-create'
    )
]
