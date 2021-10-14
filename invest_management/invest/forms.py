from django import forms
from django.utils import timezone
import datetime

class ExpenditureForm(forms.Form):
    invest_date = forms.DateField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "date_choice",
                "style": "width:120px",
                "placeholder": "日付",
            }
        )
    )

    topix_price = forms.IntegerField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "style": "width:100px",
                "placeholder": "株価",
            }
        )
    )

    topix_invest = forms.IntegerField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "style": "width:100px",
                "placeholder": "購入額",
            }
        )
    )

    developed_price = forms.IntegerField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "style": "width:100px",
                "placeholder": "株価",
            }
        )
    )

    developed_invest = forms.IntegerField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "style": "width:100px",
                "placeholder": "購入額",
            }
        )
    )

    developing_price = forms.IntegerField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "style": "width:100px",
                "placeholder": "株価",
            }
        )
    )

    developing_invest = forms.IntegerField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "style": "width:100px",
                "placeholder": "購入額",
            }
        )
    )

    all_price = forms.IntegerField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "style": "width:100px",
                "placeholder": "株価",
            }
        )
    )

    all_invest = forms.IntegerField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "style": "width:100px",
                "placeholder": "購入額",
            }
        )
    )
