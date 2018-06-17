from django import forms

from rankings.models import Event


class MergeAthletesForm(forms.Form):
    first_athlete = forms.CharField(label='First athlete (will be kept)')
    second_athlete = forms.CharField(label='Second athlete (will be removed)')


class AddResultForm(forms.Form):
    event = forms.ModelChoiceField(queryset=Event.objects.all())
    time = forms.DurationField(label='Time', widget=forms.TextInput(attrs={'placeholder': '00:00.00'}))
    date = forms.DateField(label='Date', widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
