import math

from django.core import serializers
from django.db.models import Sum
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_list_or_404, get_object_or_404, render

from nfc_card_game.main.color import (
    ALL_COLOR_UUID,
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

ABS_SELL_OPTIONS = [1, 5, 10, 20, 50, 100, 500, 1000, 5000, 10000]
REL_SELL_OPTIONS = {1: "100%", 0.5: "50%", 0.25: "25%"}


def index(request):
    return HttpResponse("Scan een kaartje met je telefoon!")

def thanks(request, card_uuid):
    return render(request, "thanks.html")


def get_player_register(request: HttpRequest, card_uuid: str):
    player_instance, _ = Player.objects.get_or_create(card_uuid=card_uuid)
    form = PlayerForm(instance=player_instance)
    return render(request, "register.html", {"form": form})


def handle_activities_player(
    request: HttpRequest, player: Player, game_mode: GameSettings.GameMode
) -> HttpResponse:
    if act_uuid := request.session.get("post"):
        if act_uuid == "vote":
            return render(request, "activities/vote.html")

        activity = Activity.objects.get(card_uuid=act_uuid)
        player.activities.add(activity)

    all_activities = {act: False for act in Activity.objects.all()}
    player_activities = list(player.activities.all())
    for player_act in player_activities:
        all_activities[player_act] = True

    if game_mode == GameSettings.GameMode.VOSSENJACHT:
        all_activities = {act: True for act, value in all_activities.items() if value}

    return render(
        request,
        "activities/overview.html",
        {
            "player_activities": all_activities,
            "player": player,
            "title": game_mode,
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
    player.name = player.name.split(" ")[0]
    context = {"buy_amount": selected_amount, "items": items, "player": player}
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

    player.name = player.name.split(" ")[0]
    context = {"player": player, "items": player_items}
    request.session.pop("price", None)

    absolute_sell_options = {}
    relative_sell_options = {}

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

            absolute_sell_options = {
                sell_option: sell_option * price
                for sell_option in ABS_SELL_OPTIONS
                if sell_option * price <= total_money
            }

            relative_sell_options = {
                math.floor((total_money / price) * factor): text
                for factor, text in REL_SELL_OPTIONS.items()
            }

        if post[0].post.type == TypeType.MINER:
            min_item_amount = min(
                player_items.get(item=recipe.item).amount for recipe in post
            )

            absolute_sell_options = {
                sell_option: sell_option * sell_option
                for sell_option in ABS_SELL_OPTIONS
                if sell_option * sell_option <= min_item_amount
            }

            relative_sell_options = {
                math.floor(min_item_amount * factor): text
                for factor, text in REL_SELL_OPTIONS.items()
            }

    if mine_uuid := request.session.get("mine"):
        mine = TeamMine.objects.filter(mine__card_uuid=mine_uuid, team=player.team)
        mine_items = TeamMineItem.objects.filter(team_mine__mine__card_uuid=mine_uuid)
        context["post"] = mine
        context["mine"] = mine
        action = handle_mine_scan(player, player_items, mine, mine_items)
        context["action"] = action.model_dump() if action else None

    absolute_sell_options.pop(0, None)
    relative_sell_options.pop(0, None)
    context["buy_amounts_abs"] = sorted(absolute_sell_options.items())
    context["buy_amounts_rel"] = sorted(relative_sell_options.items())

    return render(request, "trading/player_stats.html", context)


def player(request: HttpRequest, card_uuid: str) -> HttpResponse:
    try:
        player = Player.objects.get(card_uuid=card_uuid)
    except Player.DoesNotExist:
        player = None

    if player is None or player.name == "" or player.team is None:
        return get_player_register(request, card_uuid)

    game_mode = GameSettings.object().mode
    if game_mode == GameSettings.GameMode.TRADING:
        return handle_trading_player(request, player)

    if game_mode in [
        GameSettings.GameMode.ACTIVITIES,
        GameSettings.GameMode.VOSSENJACHT,
    ]:
        return handle_activities_player(request, player, game_mode)

    if game_mode == GameSettings.GameMode.COLOR:
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


def post_trading(request, card_uuid: str) -> HttpResponse:
    post = get_object_or_404(Post, card_uuid=card_uuid)
    buys = get_list_or_404(PostRecipe, post=post.pk)
    request.session["post"] = post.card_uuid
    request.session.pop("mine", None)

    return render(request, "trading/post.html", {"post": post, "buys": buys})


def post_color(request, card_uuid: str) -> HttpResponse:
    if card_uuid in ALL_COLOR_UUID:
        request.session["post"] = card_uuid
        return render(
            request, "msg.html", {"text": f"logged in as {ALL_COLOR_UUID[card_uuid]}"}
        )

    return render(request, "msg.html", {"text": "Geen kleur gevonden op deze kaart!"})


def post_activities(request: HttpRequest, card_uuid: str) -> HttpResponse:
    if card_uuid == "vote":
        request.session["post"] = card_uuid
        return render(request, "msg.html", {"text": "logged in as stembus"})

    activity = get_object_or_404(Activity, card_uuid=card_uuid)
    request.session["post"] = card_uuid
    return render(request, "msg.html", {"text": f"logged in as {activity.name}"})


def post(request: HttpRequest, card_uuid: str) -> HttpResponse:
    game_mode = GameSettings.object().mode
    if game_mode == GameSettings.GameMode.TRADING:
        return post_trading(request, card_uuid)

    if game_mode == GameSettings.GameMode.COLOR:
        return post_color(request, card_uuid)

    if game_mode in [
        GameSettings.GameMode.ACTIVITIES,
        GameSettings.GameMode.VOSSENJACHT,
    ]:
        return post_activities(request, card_uuid)


def dashboard(request: HttpRequest) -> HttpResponse:
    pi = serializers.serialize("json", PlayerItem.objects.all())
    tm = TeamMine.objects.all().order_by("team", "mine__currency")
    tmi = TeamMineItem.objects.all().order_by(
        "team_mine__team", "item__currency", "item"
    )
    data = {"player_items": pi, "team_mines": tm, "team_mine_items": tmi}
    return render(request, "trading/dashboard.html", data)


def clear_session(request: HttpRequest) -> HttpRequest:
    request.session.pop("post", None)
    request.session.pop("mine", None)
    return render(request, "msg.html", {"text": "Cleared session"})
