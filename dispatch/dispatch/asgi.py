"""
ASGI config for dispatch project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

# import os
# import django
# from channels.routing import get_default_application
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dispatch.settings')
# django.setup()
# application = get_default_application()


import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from dispatch.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dispatch.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(  # Ensure users are authenticated if needed
        URLRouter(
            websocket_urlpatterns  # Connect WebSocket to the routing
        )
    ),
})