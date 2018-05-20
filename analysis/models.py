from datetime import timedelta

from django.db import models
from django.db.models import ForeignKey, Count

from rankings.models import Event, Athlete
from django.contrib.auth.models import User


class SpecialResult(models.Model):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2
    GENDER_CHOICES = (
        (UNKNOWN, 'Unknown'),
        (MALE, 'Male'),
        (FEMALE, 'Female')
    )

    gender = models.IntegerField(default=UNKNOWN, choices=GENDER_CHOICES)

    event = ForeignKey(Event, on_delete=models.CASCADE)
    time = models.DurationField()

    def __str__(self):
        return self.time


class AnalysisGroup(models.Model):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2
    GENDER_CHOICES = (
        (UNKNOWN, 'Unknown'),
        (MALE, 'Male'),
        (FEMALE, 'Female')
    )

    gender = models.IntegerField(default=UNKNOWN, choices=GENDER_CHOICES)

    name = models.CharField(max_length=60)
    creator = ForeignKey(User, on_delete=models.SET_NULL, null=True)
    public = models.BooleanField(default=False)
    athlete = models.ManyToManyField(Athlete)

    def get_group_teams_with_full_setup(self):
        num_events = Event.objects.filter(type=3).count()
        group_teams = GroupTeam.objects.annotate(num_setups=Count('setups')).filter(num_setups=num_events,
                                                                                    analysis_group=self).all()
        return group_teams

    def delete_all_previous_analysis(self):
        group_teams = GroupTeam.objects.filter(analysis_group=self)
        for group_team in group_teams:
            setups = group_team.setups.all()
            setups.delete()
        group_teams.delete()


class GroupEventSetup(models.Model):
    athletes = models.ManyToManyField(Athlete)
    event = ForeignKey(Event, on_delete=models.CASCADE)
    time = models.DurationField()


class GroupTeam(models.Model):
    analysis_group = ForeignKey(AnalysisGroup, on_delete=models.SET_NULL, null=True)
    athletes = models.ManyToManyField(Athlete)
    setups = models.ManyToManyField(GroupEventSetup)

    def get_total_time(self):
        setups = self.setups.all()
        total_time = timedelta(0)
        for setup in setups:
            total_time += setup.time
        return total_time

    def get_ordered_setups(self):
        return self.setups.order_by('event')
