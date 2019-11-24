from django.db import models


class CommunityAd(models.Model):
    title = models.CharField(max_length=24)
    content = models.CharField(max_length=140)
    url = models.URLField(null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
