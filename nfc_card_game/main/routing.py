from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from nfc_card_game.consumers import MessageConsumer

application = ProtocolTypeRouter({
    'websocket': URLRouter([
        path('ws/', MessageConsumer.as_asgi())
    ])
})

channel_routing = [
    re_path(r"ws/", consumers.WSConsumer.as_asgi()),
    re_path(r"ws/", consumers.MyMqttConsumer.as_asgi())
]
