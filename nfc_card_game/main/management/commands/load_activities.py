from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from nfc_card_game.main.models.activities import Activity
from nfc_card_game.main.models.player import Player


class Command(BaseCommand):
    help = "Load activites from csv"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str)

    def handle(self, *args, **options):
        with Path(options.get("file")).open("r") as fp:
            lines = fp.readlines()

        Activity.objects.all().delete()

        for line in lines[1:]:
            name, uuid = line.split(",")
            print(name, uuid)
            Activity(name=name, card_uuid=uuid).save()
