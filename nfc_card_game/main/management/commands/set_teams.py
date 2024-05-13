from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from nfc_card_game.main.models.player import Player, Team


class Command(BaseCommand):
    help = "Asign every player to a team"

    def handle(self, *args, **options):
        players = Player.objects.all()
        teams = Team.objects.all()

        i = 0
        for player in players:
            player.team = teams[i % len(teams)]
            print(f"{player.name}: {player.team}")
            player.save()
            i += 1
