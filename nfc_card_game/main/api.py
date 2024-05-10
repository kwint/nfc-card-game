from django.core import serializers
from django.db.models import Sum
from django.http import Http404, HttpRequest, JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render

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

    # Extract and structure mine stats
    # mines -> teams -> items
    data_mines = {}
    for mine in Mine.objects.all():
        data_teams = {};
        for team_mine in mine.teammine_set.all():
            data_items = []
            for item in team_mine.teammineitem_set.all().order_by("item_id"):
                data_items.append({
                    "name": item.item.name,
                    "amount": item.amount,
                    # TODO: expose effective amount here?
                    "effective": item.amount,
                });

            data_teams[team_mine.team_id] = {
                "money": team_mine.money,
                "items": data_items,
            };

        data_mines[mine.id] = {
            "name": mine.name,
            "teams": data_teams,
        };

    return JsonResponse({
        "mines": data_mines,
    });