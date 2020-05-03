from django.conf import settings
from django.conf.urls import url  # For django versions before 2.0
from django.urls import include, path  # For django versions from 2.0 and up
from django.contrib import admin

from lifesaving_rankings.views import ultimate_lifesaver, rankings_redirect, about
from rankings import views

urlpatterns = [
    path('', views.FrontPageRecords.as_view(), name='home'),
    url('', include('rankings.urls')),
    url(r'^rankings/*', rankings_redirect),
    url(r'^accounts/', include('allauth.urls')),
    url(regex=r'^accounts/profile/',
        view=views.FrontPageRecords.as_view(),
        name='profile'),
    url(r'^analysis/', include('analysis.urls')),
    url(r'^ultimate-lifesaver/', ultimate_lifesaver),
    url(r'^about/', about),
    url(r'^admin/', admin.site.urls),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

handler404 = 'lifesaving_rankings.views.error_404_view'
handler500 = 'lifesaving_rankings.views.error_500_view'
