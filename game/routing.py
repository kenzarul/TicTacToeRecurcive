from django.urls import path, re_path
from game.consumers import GameConsumer


websocket_urlpatterns = [
    re_path(r"ws/game/(?P<room_code>\w+)/$", GameConsumer.as_asgi()),
]

