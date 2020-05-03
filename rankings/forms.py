from django import forms

from rankings.models import Event


class MergeAthletesForm(forms.Form):
    first_athlete = forms.CharField(label='First athlete (will be kept)')
    second_athlete = forms.CharField(label='Second athlete (will be removed)')


class AddResultForm(forms.Form):
    event = forms.ModelChoiceField(queryset=Event.objects.all())  # TODO: filter out relays
    time = forms.DurationField(label='Time', widget=forms.TextInput(attrs={'placeholder': '00:00.00'}))
    date = forms.DateField(label='Date', widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))


class RequestCompetitionForm(forms.Form):
    competition_name = forms.CharField(label='Competition name*')
    link_to_results = forms.CharField(label='Link to results', required=False)
    competition_date = forms.CharField(label='Competition date', required=False)
    location = forms.CharField(label='Location', required=False)
    your_email = forms.CharField(label='Your email (for additional questions and updates)', required=True)

