"""lifesaving_rankings URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from lifesaving_rankings.views import ultimate_lifesaver, rankings_redirect, about
from rankings import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.FrontPageRecords.as_view(),
        name='home'
    ),
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

    url(r'^djga/', include('google_analytics.urls')),
]

handler404 = 'lifesaving_rankings.views.error_404_view'
handler500 = 'lifesaving_rankings.views.error_500_view'
