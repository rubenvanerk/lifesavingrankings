from django import forms
from django.conf import settings

from rankings.models import Event


class AddResultForm(forms.Form):
    event = forms.ModelChoiceField(
        queryset=Event.objects.filter(type__in=[Event.INDIVIDUAL, Event.RELAY_SEGMENT]),
        widget=forms.Select(attrs={'class': 'ui default search dropdown'})
    )
    time = forms.DurationField(label='Time',
                               widget=forms.TextInput(attrs={
                                   'placeholder': '00:00.00',
                                   'class': 'time'
                               }))
    date = forms.DateField(label='Date', input_formats=[settings.DATE_INPUT_FORMAT],
                           widget=forms.TextInput(attrs={'class': 'ui calendar', 'placeholder': 'Date'}))


class RequestCompetitionForm(forms.Form):
    competition_name = forms.CharField(label='Competition name*')
    link_to_results = forms.CharField(label='Link to results', required=False)
    competition_date = forms.CharField(label='Competition date', required=False)
    location = forms.CharField(label='Location', required=False)
    your_email = forms.CharField(label='Your email (for additional questions and updates)', required=True)
