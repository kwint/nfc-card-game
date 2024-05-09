from django import forms


from nfc_card_game.main.models.player import Player


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ["card_uuid", "name", "section"]


class BuyAmountForm(forms.Form):
    amount = forms.IntegerField()
