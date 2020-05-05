from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from . import views
from rankings import views as rankings_views

urlpatterns = [
    path('', rankings_views.FrontPageRecords.as_view(), name='home'),

    path('about/', views.about),
    path('changelog/', views.changelog),
    path('ultimate-lifesaver/', views.ultimate_lifesaver),

    path('', include('rankings.urls')),
    path('analysis/', include('analysis.urls')),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),

    path('rankings<path:path>', views.rankings_redirect),
    path('accounts/profile/', rankings_views.FrontPageRecords.as_view(), name='profile'),  # TODO: replace with actual profile
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

handler404 = 'lifesaving_rankings.views.error_404_view'
handler500 = 'lifesaving_rankings.views.error_500_view'
