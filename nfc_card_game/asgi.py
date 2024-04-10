"""
ASGI config for nfc_card_game project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

from channels.routing import ProtocolTypeRouter, URLRouter

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nfc_card_game.settings")

application = get_asgi_application()

import nfc_card_game.routing
from nfc_card_game.routing import channel_routing

application = ProtocolTypeRouter({
    "http": asgi_application,
    "websocket": URLRouter(websocket_urlpatterns)
})
