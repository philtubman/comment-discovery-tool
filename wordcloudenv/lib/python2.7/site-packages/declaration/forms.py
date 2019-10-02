from django import forms


class DeclarationForm(forms.Form):
    next = forms.CharField(widget=forms.HiddenInput, required=False)
