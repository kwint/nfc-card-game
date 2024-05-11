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
    """
    Expose all game stats for the dashboard.
    """

    return JsonResponse(describe_mines())


def dashboard_mine(request: HttpRequest, mine_id: int) -> JsonResponse:
    """
    Expose stats of a specific mine to the dashboard.
    """

    mine = Mine.objects.get(id=mine_id)
    return JsonResponse(describe_mine(mine))


def describe_mines():
    """
    Describe the stats for all mines in a way that the dashboard understands.
    """
    data_mines = {}
    for mine in Mine.objects.all():
        data_mines[mine.id] = describe_mine(mine)
    return {"mines": data_mines}


def describe_mine(mine: Mine | int):
    """
    Describe the stats of a mine in a way that the dashboard understands.
    """

    # If an ID is provided, fetch the mine object
    if isinstance(mine, int):
        mine = Mine.objects.get(id=mine)

    data_teams = {}
    for team_mine in mine.teammine_set.all():
        data_items = []
        for item in team_mine.teammineitem_set.all().order_by("item_id"):
            data_items.append({
                "name": item.item.name,
                "amount": item.amount,
                # TODO: expose effective amount here?
                "effective": item.amount,
            })

        data_teams[team_mine.team_id] = {
            "money": team_mine.money,
            "items": data_items,
        }

    return {
        "name": mine.name,
        "teams": data_teams,
    }
