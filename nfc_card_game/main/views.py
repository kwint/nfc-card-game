from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Player


def index(request):
    return HttpResponse("Hello, world. You're at the main index.")


def player(request, card_uuid):
    player = get_object_or_404(Player, card_uuid=card_uuid)
    return render(request, "scan.html", {"player": player})
