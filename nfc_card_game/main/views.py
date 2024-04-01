from django.contrib.auth import login
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from nfc_card_game.main.logic import execute_transaction

from .models import Player, Post


def index(request):
    return HttpResponse("Hello, world. You're at the main index.")


def player(request, card_uuid):
    player = get_object_or_404(Player, card_uuid=card_uuid)

    action: dict[str, str | int] | None = None
    if post_uuid := request.session.get("post"):
        post = get_object_or_404(Post, card_uuid=post_uuid)
        action = execute_transaction(player, post)

    return render(request, "player_stats.html", {"player": player, "action": action})


def post(request, card_uuid):
    post = get_object_or_404(Post, card_uuid=card_uuid)
    request.session["post"] = post.card_uuid
    return HttpResponse(f"{post.name} logged in")
