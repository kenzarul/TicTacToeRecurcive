import os
import django  # ⬅️ Must be imported explicitly
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tictactoe.settings')

# ⬅️ Set up Django before importing models, routes, etc.
django.setup()

import game.routing  # ⬅️ Now safe to import app modules

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            game.routing.websocket_urlpatterns
        )
    ),
})


print("ASGI router loaded")
