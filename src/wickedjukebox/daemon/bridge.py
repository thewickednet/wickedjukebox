from django.apps import apps

from wickedjukebox.daemon.model import QueueMessage


class Bridge:
    @staticmethod
    def send_message(appname: str, message: QueueMessage) -> None:
        config = apps.get_app_config(appname)
        config.procinfo.queue.put(message)
