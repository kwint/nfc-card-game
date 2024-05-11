from django.urls import path

from . import api
from . import views
from . import game_loop

urlpatterns = [
    path("", views.index, name="index"),
    path("player/<str:card_uuid>", views.player, name="player"),
    path("post/<str:card_uuid>", views.post, name="post"),
    path("dashboard", views.dashboard, name="dasbhoard"),
    path("mine/<str:card_uuid>", views.mine, name="mine"),
    path("register-player/", views.register_player, name="register-player"),
    path("stop-game-loop", game_loop.stop_scheduler, name="stop-game-loop"),
    path("start-game-loop", game_loop.start_scheduler, name="start-game-loop"),
    path("api/dashboard", api.dashboard, name="api/dashboard"),
    path("api/dashboard/<int:mine_id>", api.dashboard_mine, name="api/dashboard/mine"),
]
