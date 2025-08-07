from django.urls import re_path
from your_app_name import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),  # Path for WebSocket connection
]