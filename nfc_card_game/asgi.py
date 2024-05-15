"""
ASGI config for nfc_card_game project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import django
from channels.routing import ProtocolTypeRouter, URLRouter
import os
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nfc_card_game.settings")

django.setup()

from nfc_card_game.main.consumers import MessageConsumer
from nfc_card_game.main.api_consumer import ApiConsumer

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    path("ws/", MessageConsumer.as_asgi()),
                    path("api/ws", ApiConsumer.as_asgi()),
                ]
            )
        ),
    }
)
