import ast
import json

from django import forms

from analysis.models import AnalysisGroup


class ChooseFromDateForm(forms.Form):
    from_date = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))


class AnalysisGroupForm(forms.ModelForm):
    athlete = forms.CharField(widget=forms.SelectMultiple(attrs={'id': 'select-athletes', 'class': 'ui dropdown search selection multiple'}))

    def clean_athlete(self):
        athlete = self.cleaned_data['athlete']
        athlete = ast.literal_eval(athlete)
        return athlete

    class Meta:
        model = AnalysisGroup
        fields = ['name', 'athlete', 'public', 'gender']

    def __init__(self, *args, **kwargs):
        super(AnalysisGroupForm, self).__init__(*args, **kwargs)
        fomantic_dropdown_values = []
        for athlete in self.instance.athlete.all():
            fomantic_dropdown_values.append({'name': athlete.name, 'value': str(athlete.pk)})
        self.fields['athlete'].widget.attrs['data-values'] = json.dumps(fomantic_dropdown_values)

