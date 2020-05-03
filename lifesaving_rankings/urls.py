from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from lifesaving_rankings.views import ultimate_lifesaver, rankings_redirect, about
from rankings import views

urlpatterns = [
    path('', views.FrontPageRecords.as_view(), name='home'),
    path('', include('rankings.urls')),
    path('rankings<path:path>', rankings_redirect),
    path('accounts/', include('allauth.urls')),
    path('accounts/profile/', views.FrontPageRecords.as_view(), name='profile'),  # TODO: replace with actual profile
    path('analysis/', include('analysis.urls')),
    path('ultimate-lifesaver/', ultimate_lifesaver),
    path('about/', about),
    path('admin/', admin.site.urls),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

handler404 = 'lifesaving_rankings.views.error_404_view'
handler500 = 'lifesaving_rankings.views.error_500_view'
