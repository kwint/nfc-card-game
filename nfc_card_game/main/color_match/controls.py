from django.http import HttpRequest, HttpResponse

from nfc_card_game.main.color_match.models import (
    ColorMatchGameState,
    ColorMatchSettings,
)
from nfc_card_game.main.models.player import Player


def reset_and_start_game(request: HttpRequest) -> HttpResponse:
    if ColorMatchSettings.object().game_state != ColorMatchGameState.STOPPED:
        return HttpResponse("Please stop game first")

    Player.objects.all().update(color=None, color_points=0)
    game_settings = ColorMatchSettings.object()
    game_settings.game_state = ColorMatchGameState.RUNNING
    game_settings.save()

    return HttpResponse("Color game resetted, new game can be started imediatly!")


def stop_game(request: HttpRequest) -> HttpResponse:
    game_settings = ColorMatchSettings.object()
    game_settings.game_state = ColorMatchGameState.STOPPED
    game_settings.save()

    return HttpResponse("Color game stopped")


def start_game(request: HttpRequest) -> HttpResponse:
    game_settings = ColorMatchSettings.object()
    game_settings.game_state = ColorMatchGameState.RUNNING
    game_settings.save()

    return HttpResponse("Color game started, this action did <b>not</b> reset points")
