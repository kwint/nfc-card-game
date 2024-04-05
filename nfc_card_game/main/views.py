from django.http import HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, render, get_list_or_404

from .logic import ActionInfo, handle_mine_scan, handle_post_scan
from .models import Player, Post, TeamMine, PostRecipe, PlayerItem


def index(request):
    return HttpResponse("Hello, world. You're at the main index.")


def player(request: HttpRequest, card_uuid: str) -> HttpResponse:
    player = get_object_or_404(Player, card_uuid=card_uuid)
    player_item = PlayerItem.objects.filter(player=player)
    items = player.playeritem_set.all()

    action: ActionInfo | None = None
    if post_uuid := request.session.get("post"):
        post_recipes = PostRecipe.objects.filter(post__card_uuid=post_uuid)
        action = handle_post_scan(player, post_recipes, player_item)

    if mine_uuid := request.session.get("mine"):
        mine = get_object_or_404(TeamMine, card_uuid=mine_uuid)
        action = handle_mine_scan(player_item, player, mine)

    action_dict = action.model_dump() if action else None
    return render(
        request, "player_stats.html", {"player": player, "action": action_dict, "items": items}
    )


def post(request: HttpRequest, card_uuid: str) -> HttpResponse:
    post = get_object_or_404(Post, card_uuid=card_uuid)
    buys = get_list_or_404(PostRecipe, post=post.pk)
    request.session["post"] = post.card_uuid
    request.session.pop("mine", None)


    return render(request, "post.html", {"post": post, "buys": buys})
    return HttpResponse(f"{post.name} logged in")


def mine(request: HttpRequest, card_uuid: str) -> HttpResponse:
    mine = get_object_or_404(TeamMine, card_uuid=card_uuid)
    request.session["mine"] = mine.card_uuid
    request.session.pop("post", None)
    return HttpResponse(f"{mine.mine.name} for {mine.team.name} logged in")
