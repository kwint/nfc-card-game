from django.http import HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, render, get_list_or_404
from django.core import serializers

from .logic import ActionInfo, handle_post_scan
from .models import Player, Post, TeamMine, PostRecipe, PlayerItem


def index(request):
    return HttpResponse("Hello, world. You're at the main index.")


def player(request: HttpRequest, card_uuid: str) -> HttpResponse:
    player = get_object_or_404(Player, card_uuid=card_uuid)
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
    template_data["post"] = post
    return render(request, "player_stats.html", template_data)


def post(request: HttpRequest, card_uuid: str) -> HttpResponse:
    post = get_object_or_404(Post, card_uuid=card_uuid)
    buys = get_list_or_404(PostRecipe, post=post.pk)
    request.session["post"] = post.card_uuid
    request.session.pop("mine", None)

    return render(request, "post.html", {"post": post, "buys": buys})


def dashboard(request: HttpRequest) -> HttpResponse:
    pi = serializers.serialize("json", PlayerItem.objects.all())
    tm = TeamMine.objects.all()
    data = {"player_items": pi, "team_mines": tm}
    print(data)
    return render(request, "dashboard.html", data)
