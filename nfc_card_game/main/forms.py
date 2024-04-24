from django.forms import ModelForm

from nfc_card_game.main.models import Player

class PlayerForm(ModelForm):
    class Meta:
        model = Player
        fields = ["card_uuid", "name", "section"]