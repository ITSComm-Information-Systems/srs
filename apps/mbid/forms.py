from django import forms
from datetime import date, datetime


class createCycle(forms.Form):
    bidYear = forms.CharField(label='Bidding Year', widget=forms.Select(
        choices=[(x, x) for x in range(date.today().year, date.today().year+3)]))

    bidMonth = forms.CharField(label='Bidding Month', widget=forms.Select(choices=((x, x) for x in [
        'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])))

    openDate = forms.CharField(label='Bidding Open Date', widget=forms.DateInput(attrs={'type': 'date'}))
    closeDate = forms.CharField(label='Bidding Close Date', widget=forms.DateInput(attrs={'type': 'date'}))