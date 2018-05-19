from django import forms


class MergeAthletesForm(forms.Form):
    first_athlete = forms.CharField(label='First athlete (will be kept)')
    second_athlete = forms.CharField(label='Second athlete (will be removed)')
