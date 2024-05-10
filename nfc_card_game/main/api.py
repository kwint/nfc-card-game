from django.core import serializers
from django.http import Http404, HttpRequest, JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.db.models import Sum

from nfc_card_game.main.color import (
    COLOR_HOME_UUID,
    COLOR_JOKER_UUID,
    COLOR_UUID,
    give_player_color,
    post_correct_color,
    post_wrong_color,
    remove_player_color,
)
from nfc_card_game.main.forms import PlayerForm
from nfc_card_game.main.models.trading import TypeType
from nfc_card_game.main.models.activities import Activity
from nfc_card_game.main.models.game_settings import GameSettings
from copy import copy
from .logic import (
    get_resource_price,
    handle_mine_scan,
    handle_miner_scan,
    handle_post_scan,
)
from .models.player import Player
from .models.trading import Mine, PlayerItem, Post, PostRecipe, TeamMine, TeamMineItem


def dashboard(request: HttpRequest) -> JsonResponse:
    pi = serializers.serialize("json", PlayerItem.objects.all())
    tm = TeamMine.objects.all().order_by("team", "mine__currency")
    tmi = TeamMineItem.objects.all().order_by(
        "team_mine__team", "item__currency", "item"
    )
    # data = {"player_items": pi, "team_mines": tm, "team_mine_items": tmi}
    data = {"mines": [1000, 2000]}
    return JsonResponse(data);
