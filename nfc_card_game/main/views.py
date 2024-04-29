from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.core import serializers

from nfc_card_game.main.forms import PlayerForm
from nfc_card_game.main.models.activities import Activity
from nfc_card_game.main.models.game_settings import GameSettings

from .logic import ActionInfo, handle_post_scan
from .models.player import Player
from .models.trading import PlayerItem, Post, PostRecipe, TeamMine


def index(request):
    return HttpResponse("Hello, world. You're at the main index.")


def get_player_register(request: HttpRequest):
    form = PlayerForm(player)
    return render(request, "register.html", {"form": form})


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

    action_dict = action.model_dump() if action else None
    template_data["action"] = action_dict
    return render(request, "trading/player_stats.html", template_data)


def handle_activities_player(request: HttpRequest, player: Player) -> HttpResponse:
    if act_uuid := request.session.get("post"):
        activity = Activity.objects.filter(card__uuid=act_uuid)
        player.activities.add(activity)

    all_activities = list(Activity.objects.all())
    player_activities = list(player.activities.all())
    remaining = [
        activity for activity in all_activities if activity not in player_activities
    ]

    return render(request, "activities/overview.html", {"remaining": remaining, "player_activities": player_activities, "player": player})


def player(request: HttpRequest, card_uuid: str) -> HttpResponse:
    try:
        player = Player.objects.get(card_uuid=card_uuid)
    except Player.DoesNotExist:
        player = None

    if player is None or player.name == "":
        return get_player_register(request)

    if GameSettings.object().mode == GameSettings.GameMode.TRADING:
        return handle_trading_player(request, player)

    if GameSettings.object().mode == GameSettings.GameMode.ACTIVITIES:
        return handle_activities_player(request, player)


def register_player(request: HttpRequest):
    if request.method == "POST":
        form = PlayerForm(request.POST)
        if form.is_valid():
            player = form.save()
            return HttpResponseRedirect(f"/player/{player.card_uuid}")
        return HttpResponse(form.errors.as_json())

    raise Http404


def post(request: HttpRequest, card_uuid: str) -> HttpResponse:
    post = get_object_or_404(Post, card_uuid=card_uuid)
    buys = get_list_or_404(PostRecipe, post=post.pk)
    request.session["post"] = post.card_uuid
    request.session.pop("mine", None)

    return render(request, "trading/post.html", {"post": post, "buys": buys})


def dashboard(request: HttpRequest) -> HttpResponse:
    pi = serializers.serialize("json", PlayerItem.objects.all())
    tm = TeamMine.objects.all()
    data = {"player_items": pi, "team_mines": tm}
    print(data)
    return render(request, "trading/dashboard.html", data)
