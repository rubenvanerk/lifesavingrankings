from datetime import timedelta

from django.db import models
from django.db.models import ForeignKey, Count

from rankings.models import Event, Athlete
from django.contrib.auth.models import User


class SpecialResultGroup(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name


class SpecialResult(models.Model):
    event = ForeignKey(Event, on_delete=models.CASCADE)
    time = models.DurationField()
    special_result_group = models.ForeignKey(SpecialResultGroup, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.special_result_group.name + ': ' + self.event.name


class AnalysisGroup(models.Model):
    name = models.CharField(max_length=60)
    creator = ForeignKey(User, on_delete=models.SET_NULL, null=True)
    public = models.BooleanField(default=False)
    athletes = models.ManyToManyField(Athlete)
    simulation_in_progress = models.BooleanField(default=False)
    simulation_date_from = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        ordering = ('pk',)

    def get_group_teams_with_full_setup(self):
        num_events = Event.objects.filter(type=Event.RELAY_COMPLETE).count()
        group_teams = GroupTeam.objects.annotate(num_setups=Count('setups')).filter(num_setups=num_events,
                                                                                    analysis_group=self).all()
        return group_teams

    def count_group_teams_without_full_setup(self):
        num_events = Event.objects.filter(type=Event.RELAY_COMPLETE).count()
        group_team_count = GroupTeam.objects.annotate(num_setups=Count('setups')).filter(num_setups__lt=num_events)\
            .filter(analysis_group=self).count()
        return group_team_count

    def delete_all_previous_analysis(self):
        group_teams = GroupTeam.objects.filter(analysis_group=self)
        for group_team in group_teams:
            setups = group_team.setups.all()
            setups.delete()
        group_teams.delete()

    relay_analysis_is_available = None

    def relay_analysis_available(self):
        if self.relay_analysis_is_available is None:
            group_teams = list(self.groupteam_set.all().order_by('analysis_group__groupteam'))
            if len(group_teams) is 0:
                self.relay_analysis_is_available = False
                return self.relay_analysis_is_available
            last_group_team = group_teams[-1]
            self.relay_analysis_is_available = len(list(last_group_team.setups.all())) > 0
        return self.relay_analysis_is_available

    def clean_teams(self):
        self.remove_unused_athletes_from_teams()
        self.delete_duplicate_teams()

    def remove_unused_athletes_from_teams(self):
        for group_team in self.groupteam_set.all():
            group_team.remove_unused_athletes()

    def delete_duplicate_teams(self):
        for group_team in self.groupteam_set.all():
            qs = self.groupteam_set.exclude(pk=group_team.pk)
            qs = qs.annotate(athlete_count=Count('athletes')).filter(athlete_count=group_team.athletes.count())
            for athlete in group_team.athletes.all():
                qs = qs.filter(athletes__pk=athlete.pk)
            qs.delete()


class GroupEventSetup(models.Model):
    athletes = models.ManyToManyField(Athlete, through='GroupEvenSetupSegment')
    event = ForeignKey(Event, on_delete=models.CASCADE)
    time = models.DurationField()

    def get_athletes_ordered_by_index(self):
        return self.athletes.all().order_by('groupevensetupsegment__index')


class GroupEvenSetupSegment(models.Model):
    athlete = ForeignKey(Athlete, on_delete=models.CASCADE)
    group_event_setup = ForeignKey(GroupEventSetup, on_delete=models.CASCADE)
    index = models.IntegerField()


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

    def get_used_athletes(self):
        setups = self.setups.all()
        setup_segments = GroupEvenSetupSegment.objects.filter(group_event_setup__in=setups)
        athletes = Athlete.objects.filter(groupevensetupsegment__in=setup_segments).distinct()
        return athletes

    def get_unused_athletes(self):
        used_athletes = self.get_used_athletes()
        all_athletes = self.athletes.all()
        return list(set(all_athletes) - set(used_athletes))

    def remove_unused_athletes(self):
        for unused_athlete in self.get_unused_athletes():
            self.athletes.remove(unused_athlete)
