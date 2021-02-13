from django import forms


class SearchForm(forms.Form):
    company = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Company name or ticker...'}))
