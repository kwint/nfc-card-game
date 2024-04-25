from django.apps import AppConfig
import os


class MainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nfc_card_game.main"

    def ready(self):
        from . import game_loop

        if os.environ.get("RUN_MAIN", None) != "true":
            game_loop.start_scheduler()
