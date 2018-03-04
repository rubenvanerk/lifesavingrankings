from django import forms


class MergeAthletesForm(forms.Form):
    first_athlete = forms.IntegerField(label='First athlete (will be kept)')
    second_athlete = forms.IntegerField(label='Second athlete (will be removed)')
