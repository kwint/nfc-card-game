from random import shuffle
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from nfc_card_game.main.models.player import Player, Team
from nfc_card_game.main.models.trading import PlayerItem, Item
from nfc_card_game.main.models.trading import TypeType


class Command(BaseCommand):
    help = "Initialize the inventories of all players."

    def handle(self, *args, **options):
        players = Player.objects.all()

        for player in players:
            print(f"{player.name}: {player.team}")

            # Set all player items to 0
            for item in Item.objects.all():
                PlayerItem.objects.update_or_create(item=item, player=player, defaults={'item': item, 'player': player, 'amount': 0})

            # Set one random type of coin to 50
            items = Item.objects.filter(type=TypeType.COIN)
            items(shuffle)
            item = items[0]
            PlayerItem.objects.update_or_create(item=item, player=player, defaults={'item': item, 'player': player, 'amount': 50})
