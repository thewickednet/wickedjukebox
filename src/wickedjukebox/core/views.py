from textwrap import dedent

from django import http

from wickedjukebox.daemon.bridge import Bridge
from wickedjukebox.daemon.model import QueueMessage


def home(request):
    """
    Serve an index-page which uses simple demo code to send a message to the
    daemon.
    """
    Bridge.send_message(
        "core", QueueMessage(str(request.GET.get("foo", "bar")))
    )
    return http.HttpResponse("Hello, world. You're at the core index.")


def monitor_events(request):
    """
    Return a simple HTTP view that uses EventSource to monitor events from the
    daemon. It serves mainly as inspiration and "demo" code.
    """
    return http.HttpResponse(
        dedent(
            """\
        <!DOCTYPE html>
        <html>
        <head>
        <title>EventSource demo</title>
        </head>
        <body>
        <h1>EventSource demo</h1>
        <div id="result"></div>
        <script>
        var source = new EventSource("/stream");
        source.addEventListener("backend-update", function(event) {
            // append message to div with ID #result
            document.getElementById('result').innerHTML = event.data + '<br>';
        });
        source.onerror = function(event) {
            console.log(event);
        };
        source.onopen = function(event) {
            console.log(event);
        };
        </script>
        </body>
        </html>
        """
        )
    )


def stream(request):
    """
    Serve an SSE endpoint for the JS EventSource to consume.
    """
    iterator = Bridge.daemon_messages("core")
    response = http.StreamingHttpResponse(
        iterator, content_type="text/event-stream"
    )
    response["Cache-Control"] = "no-cache"
    return response
