from django.urls import path
from apps.webssh.tools.channel import websocket, podsocket, exec
from django.urls import re_path


websocket_urlpatterns = [
    path('webssh/ssh.html', websocket.WebSSH.as_asgi()),
    path('webssh/pod.html', podsocket.StreamConsumer.as_asgi()),
    path('webssh/exec.html', exec.Exec.as_asgi())
]
