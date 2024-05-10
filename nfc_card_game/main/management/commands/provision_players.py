from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from nfc_card_game.main.models.player import Player


class Command(BaseCommand):
    help = "Load players from csv"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str)

    def handle(self, *args, **options):
        with Path(options.get("file")).open("r") as fp:
            lines = fp.readlines()

        for line in lines[1:]:
            name, section, uuid, _ = line.split(",")
            print(name, section, uuid)
            Player(name=name, section=section, card_uuid=uuid).save()
