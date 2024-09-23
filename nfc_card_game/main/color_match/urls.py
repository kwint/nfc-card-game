from nfc_card_game.main.color_match import controls
from nfc_card_game.main.color_match.color import color_overview
from django.urls import path

color_urlpatterns = [
    path("overview", color_overview, name="color_overview"),
    path("reset", controls.reset_and_start_game, name="color_reset"),
    path("stop", controls.stop_game, name="color_stop"),
    path("start", controls.start_game, name="color_start"),
]
