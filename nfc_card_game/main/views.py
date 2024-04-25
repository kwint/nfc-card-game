from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_list_or_404, get_object_or_404, render

from nfc_card_game.main.forms import PlayerForm

from .logic import ActionInfo, handle_mine_scan, handle_post_scan
from .models import Player, PlayerItem, Post, PostRecipe, TeamMine


def index(request):
    return HttpResponse("Hello, world. You're at the main index.")


def player(request: HttpRequest, card_uuid: str) -> HttpResponse:
    try:
        player = Player.objects.get(card_uuid=card_uuid)
        print(player.name)
    except Player.DoesNotExist:
        player = None

    if player is None or player.name == "":
        form = PlayerForm(player)
        return render(request, "register.html", {"form": form})


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
    return render(
            request, "player_stats.html", template_data
    )


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

    return render(request, "post.html", {"post": post, "buys": buys})


def dashboard(request: HttpRequest) -> HttpResponse:
    pi = serializers.serialize("json", PlayerItem.objects.all())
    tm = TeamMine.objects.all()
    data = {"player_items": pi, "team_mines": tm}
    print(data)
    return render(request, "dashboard.html", data)
