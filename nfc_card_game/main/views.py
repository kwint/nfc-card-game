from django.http import HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, render

from .logic import ActionInfo, handle_mine_scan, handle_post_scan
from .models import Player, Post, TeamMine


def index(request):
    return HttpResponse("Hello, world. You're at the main index.")


def player(request: HttpRequest, card_uuid: str) -> HttpResponse:
    player = get_object_or_404(Player, card_uuid=card_uuid)

    action: ActionInfo | None = None
    if post_uuid := request.session.get("post"):
        post = get_object_or_404(Post, card_uuid=post_uuid)
        action = handle_post_scan(player, post)

    if mine_uuid := request.session.get("mine"):
        mine = get_object_or_404(TeamMine, card_uuid=mine_uuid)
        action = handle_mine_scan(player, mine)

    action_dict = action.model_dump() if action else None
    return render(
        request, "player_stats.html", {"player": player, "action": action_dict}
    )


def post(request: HttpRequest, card_uuid: str) -> HttpResponse:
    post = get_object_or_404(Post, card_uuid=card_uuid)
    request.session["post"] = post.card_uuid
    request.session.pop("mine", None)

    return HttpResponse(f"{post.name} logged in")


def mine(request: HttpRequest, card_uuid: str) -> HttpResponse:
    mine = get_object_or_404(TeamMine, card_uuid=card_uuid)
    request.session["mine"] = mine.card_uuid
    request.session.pop("post", None)
    return HttpResponse(f"{mine.name} logged in")
