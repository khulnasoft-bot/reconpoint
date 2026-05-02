import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# Note: This import must come after django.setup() as it depends on Django being initialized
from .routing import websocket_urlpatterns


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reconPoint.settings")

# Initialize Django settings first
import django


django.setup()


# Remote debug setup for ASGI (daphne) development server
try:
    from reconPoint.settings import UI_REMOTE_DEBUG

    if UI_REMOTE_DEBUG:
        from debugger_setup import setup_debugger

        setup_debugger()
except (ImportError, Exception):
    pass

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)
