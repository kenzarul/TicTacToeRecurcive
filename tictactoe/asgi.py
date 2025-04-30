import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import game.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tictactoe.settings')

application = ProtocolTypeRouter({
    'http':get_asgi_application(),
    'websocket': URLRouter(
        game.routing.websocket_urlpatterns
    )
})