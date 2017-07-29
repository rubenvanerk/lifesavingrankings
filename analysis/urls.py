from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'(?P<gender>\bmen\b|\bwomen\b)',
        view=views.Analysis.as_view(),
        name='analysis'
    ),
]
