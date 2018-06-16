from django import forms

from analysis.models import AnalysisGroup


class ChooseFromDateForm(forms.Form):
    from_date = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))


class AnalysisGroupForm(forms.ModelForm):
    class Meta:
        model = AnalysisGroup
        fields = ['name', 'athlete', 'public', 'gender']
        widgets = {
            'athlete': forms.SelectMultiple(attrs={'id': 'pick-athletes'})
        }

