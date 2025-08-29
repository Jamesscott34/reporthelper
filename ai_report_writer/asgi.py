"""
ASGI config for ai_report_writer project.

It exposes the ASGI callable as a module-level variable named ``application``.
Includes WebSocket routing for real-time collaboration features.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_report_writer.settings")
django_asgi_app = get_asgi_application()

# Import WebSocket routing after Django is initialized
from breakdown.routing import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        # Django's ASGI application to handle traditional HTTP requests
        "http": django_asgi_app,
        # WebSocket chat handler
        "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)
