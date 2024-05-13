from copy import copy

from django.core import serializers
from django.db.models import Sum
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
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
from nfc_card_game.main.models.activities import Activity
from nfc_card_game.main.models.game_settings import GameSettings
from nfc_card_game.main.models.trading import TypeType

from .logic import (
    get_resource_price,
    handle_mine_scan,
    handle_miner_scan,
    handle_post_scan,
)
from .models.player import Player
from .models.trading import Mine, PlayerItem, Post, PostRecipe, TeamMine, TeamMineItem

SELL_OPTIONS = {
    1: True,
    5: True,
    10: True,
    # 20: True,
    # 50: True,
    # 100: True,
    # 500: True,
    # 1000: True,
    # 5000: True,
    # 10000: True,
}


def index(request):
    return HttpResponse("Hello, world. You're at the main index.")


def get_player_register(request: HttpRequest, card_uuid: str):
    player_instance, _ = Player.objects.get_or_create(card_uuid=card_uuid)
    form = PlayerForm(instance=player_instance)
    return render(request, "register.html", {"form": form})


def handle_activities_player(request: HttpRequest, player: Player) -> HttpResponse:
    if act_uuid := request.session.get("post"):
        activity = Activity.objects.get(card_uuid=act_uuid)
        player.activities.add(activity)

    all_activities = {act: False for act in Activity.objects.all()}
    player_activities = list(player.activities.all())
    for player_act in player_activities:
        all_activities[player_act] = True

    return render(
        request,
        "activities/overview.html",
        {
            "player_activities": all_activities,
            "player": player,
        },
    )


def handle_color_player(request: HttpRequest, player: Player) -> HttpResponse:
    post_uuid = request.session.get("post")
    if COLOR_HOME_UUID == post_uuid:
        return give_player_color(request, player)

    if COLOR_JOKER_UUID == post_uuid:
        return remove_player_color(request, player)

    if color := COLOR_UUID.get(post_uuid):
        if color == player.color:
            return post_correct_color(request, player, str(color))

        return post_wrong_color(request, player, str(color))


def handle_trading_player_post(request, player: Player, items, player_item):
    selected_amount = int(request.POST.get("amount", 1))
    price = request.session.get("price")
    context = {"buy_amount": selected_amount, "items": items}
    if post_uuid := request.session.get("post"):
        post = PostRecipe.objects.filter(post__card_uuid=post_uuid)
        context["post"] = post
        if post[0].post.type == TypeType.MINER:
            action = handle_miner_scan(player, post, player_item, selected_amount)

        elif post[0].post.type == TypeType.RESOURCE:
            action = handle_post_scan(player, post, player_item, price, selected_amount)

    action_dict = action.model_dump() if action else None
    context["action"] = action_dict
    return render(request, "trading/player_bought.html", context)


def handle_trading_player(request: HttpRequest, player: Player) -> HttpResponse:
    player_items = PlayerItem.objects.filter(player=player).order_by(
        "item__currency", "item__name"
    )
    team_mines = TeamMine.objects.filter(team=player.team)

    if request.method == "POST":
        return handle_trading_player_post(request, player, player_items, player_items)

    context = {"player": player, "items": player_items}
    request.session.pop("price", None)
    sell_options = copy(SELL_OPTIONS)

    if post_uuid := request.session.get("post"):
        post = PostRecipe.objects.filter(post__card_uuid=post_uuid)
        context["post"] = post

        if post[0].post.type == TypeType.RESOURCE:
            total_money = (
                player_items.filter(item__type=TypeType.COIN)
                .exclude(item__currency=post.first().post.sells.currency)
                .aggregate(Sum("amount"))["amount__sum"]
            )
            price = get_resource_price(team_mines, post[0].post.sells)
            context["price"] = price
            request.session["price"] = price
            for sell_option in sell_options:
                if sell_option * price > total_money:
                    sell_options[sell_option] = False

        if post[0].post.type == TypeType.MINER:
            for sell_option in sell_options:
                for recipe in post:
                    resource_items = player_items.filter(
                        item__type=TypeType.RESOURCE, item=recipe.item
                    )
                    if resource_items:
                        item_amount = resource_items[0].amount
                    else:
                        item_amount = 0

                    if sell_option * recipe.price > item_amount:
                        sell_options[sell_option] = False

    if mine_uuid := request.session.get("mine"):
        mine = TeamMine.objects.filter(mine__card_uuid=mine_uuid, team=player.team)
        context["mine"] = mine

    if mine_uuid := request.session.get("mine"):
        mine = TeamMine.objects.filter(mine__card_uuid=mine_uuid, team=player.team)
        mine_items = TeamMineItem.objects.filter(team_mine__mine__card_uuid=mine_uuid)
        context["post"] = mine
        context["mine"] = mine
        action = handle_mine_scan(player, player_items, mine, mine_items)
        action_dict = action.model_dump() if action else None
        context["action"] = action_dict

    context["buy_amounts"] = sell_options

    return render(request, "trading/player_stats.html", context)


def player(request: HttpRequest, card_uuid: str) -> HttpResponse:
    try:
        player = Player.objects.get(card_uuid=card_uuid)
    except Player.DoesNotExist:
        player = None

    if player is None or player.name == "":
        return get_player_register(request, card_uuid)

    if GameSettings.object().mode == GameSettings.GameMode.TRADING:
        return handle_trading_player(request, player)

    if GameSettings.object().mode == GameSettings.GameMode.ACTIVITIES:
        return handle_activities_player(request, player)

    if GameSettings.object().mode == GameSettings.GameMode.COLOR:
        return handle_color_player(request, player)


def register_player(request: HttpRequest):
    player_instance = Player.objects.get(card_uuid=request.POST["card_uuid"])
    if request.method == "POST":
        form = PlayerForm(request.POST, instance=player_instance)
        if form.is_valid():
            player = form.save()
            return HttpResponseRedirect(f"/player/{player.card_uuid}")
        return HttpResponse(form.errors.as_json())

    raise Http404


def mine(request: HttpRequest, card_uuid: str) -> HttpResponse:
    mine = get_object_or_404(Mine, card_uuid=card_uuid)
    request.session["mine"] = mine.card_uuid
    request.session.pop("post", None)

    return render(request, "trading/mine.html", {"mine": mine})


def post(request: HttpRequest, card_uuid: str) -> HttpResponse:
    post = get_object_or_404(Post, card_uuid=card_uuid)
    buys = get_list_or_404(PostRecipe, post=post.pk)
    request.session["post"] = post.card_uuid
    request.session.pop("mine", None)

    return render(request, "trading/post.html", {"post": post, "buys": buys})


def dashboard(request: HttpRequest) -> HttpResponse:
    pi = serializers.serialize("json", PlayerItem.objects.all())
    tm = TeamMine.objects.all().order_by("team", "mine__currency")
    tmi = TeamMineItem.objects.all().order_by(
        "team_mine__team", "item__currency", "item"
    )
    data = {"player_items": pi, "team_mines": tm, "team_mine_items": tmi}
    return render(request, "trading/dashboard.html", data)
