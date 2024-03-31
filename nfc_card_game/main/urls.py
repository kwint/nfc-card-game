from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("card/<str:card_uuid>", views.player, name="player"),
]
