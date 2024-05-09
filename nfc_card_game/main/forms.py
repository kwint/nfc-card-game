from django.forms import ModelForm, forms
from django import forms

from nfc_card_game.main.models import Player


class PlayerForm(ModelForm):
    class Meta:
        model = Player
        fields = ["card_uuid", "name", "section"]


class BuyAmountForm(forms.Form):
    amount = forms.IntegerField()
