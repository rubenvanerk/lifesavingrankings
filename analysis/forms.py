import ast
import json
from django import forms
from django.conf import settings

from analysis.models import AnalysisGroup


class ChooseFromDateForm(forms.Form):
    required = False

    def __init__(self, *args, **kwargs):
        self.required = kwargs.pop('required', False)
        super(ChooseFromDateForm, self).__init__(*args, **kwargs)

    from_date = forms.DateField(required=required, label='Only use results from', input_formats=[settings.DATE_INPUT_FORMAT],
                                widget=forms.TextInput(attrs={'class': 'ui calendar', 'placeholder': 'Date'}))


class AnalysisGroupForm(forms.ModelForm):
    athlete = forms.CharField(
        widget=forms.SelectMultiple(attrs={'id': 'select-athletes', 'class': 'ui dropdown search selection multiple'}))

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
