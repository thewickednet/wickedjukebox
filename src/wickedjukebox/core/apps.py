from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "wickedjukebox.core"

    def ready(self):
        from wickedjukebox.daemon.main import start_process

        procinfo = start_process()
        self.procinfo = procinfo
