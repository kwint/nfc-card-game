from django.core import serializers
from django.db.models import Sum
from django.http import Http404, HttpRequest, JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render
from itertools import groupby

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
    mines = list(TeamMine.objects.values());

    # Structure mines data
    data_mines = {};
    for mine_id, mines in groupby(mines, lambda m: m["mine_id"]):
        if mine_id not in data_mines:
            data_mines[mine_id] = {
                "name": "Mine " + str(mine_id),
                "teams": {},
            };
        for mine in mines:
            team_id = mine["team_id"];
            del mine["id"];
            del mine["team_id"];
            del mine["mine_id"];
            data_mines[mine_id]["teams"][team_id] = mine;

    return JsonResponse({
        "mines": data_mines,
    });
