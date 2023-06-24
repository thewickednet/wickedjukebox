from typing import Optional

from django.apps import AppConfig

from wickedjukebox.daemon.main import start_process
from wickedjukebox.daemon.model import ProcessInfo


class CoreConfig(AppConfig):
    name = "wickedjukebox.core"
    daemon: Optional[ProcessInfo] = None

    def ready(self):
        if self.daemon is None:
            self.daemon = start_process()
