from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from nfc_card_game.main.models.activities import Activity
from nfc_card_game.main.models.player import Player


class Command(BaseCommand):
    help = "Export to from csv"

    def add_arguments(self, parser):
        parser.add_argument("model", type=str)
        parser.add_argument("file", type=str)

    def handle(self, *args, **options):
        base_url = "nfc.qvdijk.nl"

        if options.get("model").upper() == "PLAYER":
            objects = Player.objects.all()
            base_url += "/player"

        elif options.get("model").upper() == "ACTIVITIES":
            objects = Activity.objects.all()
            base_url += "/post"

        lines = [
            f"LINK_RECORD,{base_url}/{object.card_uuid.strip()},URL\n"
            for object in objects
        ]

        with Path(options.get("file")).open("w") as fp:
            fp.writelines(lines)
