from itertools import groupby
import random
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from nfc_card_game.main.color_match.models import (
    ColorMatchGameState,
    ColorMatchSettings,
)


from ..models.player import Player

COLOR_HOME_UUID = "home"
COLOR_JOKER_UUID = "joker"


COLOR_UUID = {
    "red": Player.Color.RED,
    "blue": Player.Color.BLUE,
    "green": Player.Color.GREEN,
    "yellow": Player.Color.YELLOW,
}

ALL_COLOR_UUID = {
    **COLOR_UUID,
    COLOR_HOME_UUID: "home",
    COLOR_JOKER_UUID: "joker",
}


def handle_color_player(request: HttpRequest, player: Player) -> HttpResponse:
    if ColorMatchSettings.object().game_state != ColorMatchGameState.RUNNING:
        return render(request, "color/stopped.html")

    post_uuid = request.session.get("post")
    if COLOR_HOME_UUID == post_uuid:
        return give_player_color(request, player)

    if player.color is None:
        return no_color(request, player)

    if COLOR_JOKER_UUID == post_uuid:
        return remove_player_color(request, player)

    if color := COLOR_UUID.get(post_uuid):
        if color == player.color:
            return post_correct_color(request, player, str(color))

        return post_wrong_color(request, player, str(color))


def give_player_color(request: HttpRequest, player: Player) -> HttpResponse:
    text = "kleur"

    if player.color is None:
        player.color = random.choice(list(Player.Color))
        player.save()
        text = "nieuwe kleur"

    return render(request, "color/home.html", {"player": player, "text": text})


def remove_player_color(request: HttpRequest, player: Player) -> HttpResponse:
    player.color = None
    player.save()

    return render(request, "color/joker.html", {"player": player})


def post_correct_color(
    request: HttpRequest, player: Player, post_color
) -> HttpResponse:
    player.color_points += 1
    player.color = None
    player.save()

    return render(
        request,
        "color/correct.html",
        {"player": player, "post_color": post_color},
    )


def post_wrong_color(request: HttpRequest, player: Player, post_color) -> HttpResponse:
    return render(
        request, "color/wrong.html", {"player": player, "post_color": post_color}
    )


def no_color(request: HttpRequest, player: Player):
    return render(request, "color/no_color.html", {"player": player})


def color_overview(request: HttpRequest) -> HttpResponse:
    players = Player.objects.all()

    player_infos = [
        {"name": player.name, "points": player.color_points, "color": player.color}
        for player in players
    ]

    player_infos = sorted(player_infos, key=lambda x: x["points"], reverse=True)
    ranking = []
    rank = 1
    rank_offset = 0
    for _, group in groupby(player_infos, lambda x: x["points"]):
        for player in group:
            ranking.append({"rank": rank} | player)
            rank_offset += 1
        rank += rank_offset
        rank_offset = 0

    return render(request, "color/overview.html", {"player_infos": ranking})


def post_color(request, card_uuid: str) -> HttpResponse:
    if card_uuid in ALL_COLOR_UUID:
        request.session["post"] = card_uuid
        return render(
            request, "msg.html", {"text": f"logged in as {ALL_COLOR_UUID[card_uuid]}"}
        )

    return render(request, "msg.html", {"text": "Geen kleur gevonden op deze kaart!"})
