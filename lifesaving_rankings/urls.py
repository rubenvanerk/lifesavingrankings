from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from analysis.views import ExtraTimesListView, AnalysisGroupListView
from . import views
from rankings import views as rankings_views
from .views import Account, Home

urlpatterns = [
    path('', Home.as_view(), name='home'),

    path('about/', views.about, name='about'),
    path('changelog/', views.changelog, name='changelog'),
    path('ultimate-lifesaver/', views.ultimate_lifesaver),

    path('', include('rankings.urls')),
    path('analysis/', include('analysis.urls')),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),

    path('rankings<path:path>', views.rankings_redirect),
    path('accounts/details/', Account.as_view(), name='account'),
    path('accounts/extra-times/', ExtraTimesListView.as_view(), name='extra-times-list'),
    path('accounts/analysis-groups/', AnalysisGroupListView.as_view(), name='private-group-list'),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

handler404 = 'lifesaving_rankings.views.error_404_view'
handler500 = 'lifesaving_rankings.views.error_500_view'
