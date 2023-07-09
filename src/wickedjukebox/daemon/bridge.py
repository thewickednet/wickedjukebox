import logging
from time import sleep
from typing import Iterable

from django.apps import apps

from wickedjukebox.core.apps import CoreConfig
from wickedjukebox.daemon.main import start_process
from wickedjukebox.daemon.model import QueueMessage

LOG = logging.getLogger(__name__)


class Bridge:
    """
    An abstraction bridge between the web and daemon process.

    This provides simple static methods to exchange messages between the web and
    daemon process. It also provides a simple way to consume messages from the
    daemon process.
    """

    @staticmethod
    def restart_subprocess(appname: str) -> None:
        config: CoreConfig = apps.get_app_config(appname)
        config.daemon.process.join(timeout=10)
        if config.daemon.process.exitcode is None:
            LOG.error("Subprocess did not stop. Will not blindly restart")
        else:
            LOG.info("Restarting the daemon process")
            start_process(config.daemon.to_daemon, config.daemon.to_web)

    @staticmethod
    def send_message(appname: str, message: QueueMessage) -> None:
        """
        Send a message to the daemon process.

        :param appname: The name of the django-app that is sending the message.
        :param message: The message to send.
        """
        config: CoreConfig = apps.get_app_config(appname)
        if config.daemon is None:
            LOG.warning("No daemon process found")
            return
        try:
            config.daemon.to_daemon.put(message)
        except Exception:
            LOG.exception("Unhandled exception in send_message")

    @staticmethod
    def daemon_messages(appname: str) -> Iterable[bytes]:
        """
        Consume messages from the daemon process.
        """
        config: CoreConfig = apps.get_app_config(appname)
        if config.daemon is None:
            LOG.warning("No daemon process found")
            return
        while True:
            try:
                msg: QueueMessage = config.daemon.to_web.get()
                sse = f"event: backend-update\ndata: {msg.to_json()}\n\n"
                yield sse.encode("utf-8")
            except Exception:
                LOG.exception("Unhandled exception in daemon_messages")
                continue
