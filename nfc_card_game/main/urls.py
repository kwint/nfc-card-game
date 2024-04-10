from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("player/<str:card_uuid>", views.player, name="player"),
    path("post/<str:card_uuid>", views.post, name="post"),
    path("dashboard", views.dashboard, name="dasbhoard"),
]
