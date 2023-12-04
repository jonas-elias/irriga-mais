from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/pivo/(?P<pivo_key>\w+)/$', consumers.ChatConsumer.as_asgi())
]
