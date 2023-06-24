from django import http

from wickedjukebox.daemon.bridge import Bridge
from wickedjukebox.daemon.model import QueueMessage


def home(request):
    Bridge.send_message("core", QueueMessage("Hello from the webapp"))
    return http.HttpResponse("Hello, world. You're at the core index.")
