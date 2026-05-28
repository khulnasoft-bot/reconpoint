import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reconPoint.settings")

# Initialize Django settings first
import django

django.setup()

# Note: This import must come after django.setup() as it depends on Django being initialized
from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application
from .routing import websocket_application




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
        "websocket": websocket_application,
    }
)
