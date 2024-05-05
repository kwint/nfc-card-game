import random
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


from .models.player import Player

COLOR_HOME_UUID = "home"
COLOR_JOKER_UUID = "joker"


COLOR_UUID = {
    "red": Player.Color.RED,
    "blue": Player.Color.BLUE,
    "green": Player.Color.GREEN,
    "yellow": Player.Color.YELLOW,
}


# COLOR_UUID = {
#     "2cac4ad8": Player.Color.RED,
#     "8e337295": Player.Color.BLUE,
#     "a8d7b7d4": Player.Color.GREEN,
#     "a4d1193c": Player.Color.YELLOW,
# }


def give_player_color(request: HttpRequest, player: Player) -> HttpResponse:
    if player.color is None:
        player.color = random.choice(list(Player.Color))
        player.save()
        text = "nieuwe kleur"

    text = "kleur"

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
