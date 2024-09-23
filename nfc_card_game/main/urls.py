from django.urls import include, path

from . import api
from . import views
from . import game_loop
from nfc_card_game.main.color_match.urls import color_urlpatterns

urlpatterns = [
    path("", views.index, name="index"),
    path("player/<str:card_uuid>", views.player, name="player"),
    path("post/<str:card_uuid>", views.post, name="post"),
    path("dashboard", views.dashboard, name="dasbhoard"),
    path("mine/<str:card_uuid>", views.mine, name="mine"),
    path("register-player/", views.register_player, name="register-player"),
    path("stop-game-loop", game_loop.stop_scheduler, name="stop-game-loop"),
    path("start-game-loop", game_loop.start_scheduler, name="start-game-loop"),
    path("clear-session", views.clear_session, name="clear-session"),
    path("api/dashboard", api.dashboard, name="api/dashboard"),
    path("api/dashboard/<int:mine_id>", api.dashboard_mine, name="api/dashboard-mine"),
    path("color/", include(color_urlpatterns)),
]
