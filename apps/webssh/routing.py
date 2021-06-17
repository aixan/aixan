from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from apps.webssh.tools.channel import routing
from django.urls import path
from django.core.asgi import get_asgi_application

application = ProtocolTypeRouter({
    # "http": get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns,
        )
    ),
})
