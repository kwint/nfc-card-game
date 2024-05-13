import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import path


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nfc_card_game.settings")
django_asgi_app = get_asgi_application()

from nfc_card_game.main.api_consumer import ApiConsumer
from nfc_card_game.main.consumers import MessageConsumer


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    [
                        path("ws/", MessageConsumer.as_asgi()),
                        path("api/ws", ApiConsumer.as_asgi()),
                    ]
                )
            )
        ),
    }
)
