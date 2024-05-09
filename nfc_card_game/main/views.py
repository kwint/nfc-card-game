from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.core import serializers

# from nfc_card_game.main.color import (
#     give_player_color,
#     post_correct_color,
#     post_wrong_color,
#     remove_player_color,
#     COLOR_HOME_UUID,
#     COLOR_JOKER_UUID,
#     COLOR_UUID,
# )
from nfc_card_game.main.forms import PlayerForm, BuyAmountForm
# from nfc_card_game.main.models.activities import Activity
# from nfc_card_game.main.models.game_settings import GameSettings

from .logic import ActionInfo, handle_post_scan, handle_mine_scan
from .models import Player
from .models import PlayerItem, Post, PostRecipe, Mine, TeamMine


def index(request):
    return HttpResponse("Hello, world. You're at the main index.")


def get_player_register(request: HttpRequest):
    form = PlayerForm(player)
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

def handle_trading_player(request: HttpRequest, player: Player) -> HttpResponse:
    player_item = PlayerItem.objects.filter(player=player)
    items = player.playeritem_set.all()
    template_data = {"player": player, "items": items}
    team_mines = TeamMine.objects.filter(team=player.team)

    action: ActionInfo | None = None
    if post_uuid := request.session.get("post"):
        post = PostRecipe.objects.filter(post__card_uuid=post_uuid)
        action = handle_post_scan(player, post, player_item, team_mines)
        template_data["post"] = post

    if mine_uuid := request.session.get("mine"):
        mine = TeamMine.objects.filter(mine__card_uuid=mine_uuid)
        action = handle_mine_scan(player, player_item, mine)
        template_data["mine"] = mine
    action_dict = action.model_dump() if action else None
    template_data["action"] = action_dict
    return render(request, "trading/player_stats.html", template_data)


def player(request: HttpRequest, card_uuid: str) -> HttpResponse:
    try:
        player = Player.objects.get(card_uuid=card_uuid)
    except Player.DoesNotExist:
        player = None

    post_uuid = request.session.get("post")
    post = PostRecipe.objects.filter(post__card_uuid=post_uuid)
    player_item = PlayerItem.objects.filter(player=player)
    team_mines = TeamMine.objects.filter(team=player.team)
    items = player.playeritem_set.all()

    if request.method == 'POST':
        selected_amount = int(request.POST.get('amount', 1))
        context = {'buy_amount': selected_amount, 'items': items}
        action = handle_post_scan(player, post, player_item, team_mines, selected_amount)
        action_dict = action.model_dump() if action else None
        context["action"] = action_dict
        return render(request, 'trading/player_bought.html', context)


    context = {"player": player, "items": items}
    context["buy_amounts"] = [1, 5, 10, 20, 50]
    context["post"] = post

    return render(request, "trading/player_stats.html", context)
    return handle_trading_player(request, player)


def register_player(request: HttpRequest):
    if request.method == "POST":
        form = PlayerForm(request.POST)
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
    print(post, buys[0].item)
    request.session["post"] = post.card_uuid
    request.session.pop("mine", None)

    return render(request, "trading/post.html", {"post": post, "buys": buys})


def dashboard(request: HttpRequest) -> HttpResponse:
    pi = serializers.serialize("json", PlayerItem.objects.all())
    tm = Mine.objects.all()
    data = {"player_items": pi, "team_mines": tm}
    print(data)
    return render(request, "trading/dashboard.html", data)
