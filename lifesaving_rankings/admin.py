from allauth.socialaccount.models import *
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site

admin.site.index_title = 'LifesavingRankings.com administration'
admin.site.site_header = 'LifesavingRankings.com administration'
admin.site.site_title = 'LifesavingRankings.com admin'

admin.site.unregister(Site)
admin.site.unregister(Group)
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialToken)
admin.site.unregister(SocialApp)
admin.site.unregister(EmailAddress)