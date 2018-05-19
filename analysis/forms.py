from django import forms


class ChooseFromDateForm(forms.Form):
    from_date = forms.DateField(widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
