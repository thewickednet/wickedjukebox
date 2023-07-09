import atexit
import logging
from multiprocessing import Process, Queue
from queue import Empty
from time import sleep
from typing import Optional

from wickedjukebox.daemon.model import ProcessInfo, QueueMessage

LOG = logging.getLogger(__name__)


def cleanup(process: Process, to_daemon: "Queue[QueueMessage]"):
    """
    Generate a cleanup function for the process.
    """

    def callback():
        LOG.debug("Daemon is cleaning up...")
        to_daemon.put(QueueMessage("exit"))
        process.join(10)
        if process.exitcode == 0:
            LOG.debug("... done")
        else:
            LOG.error("Daemon did not manage to exit cleanly!")

    return callback


def process(
    to_daemon: "Queue[QueueMessage]", to_web: "Queue[QueueMessage]"
) -> None:
    """
    A dummy implementation of the daemon process.
    """
    keep_running = True
    while keep_running:
        try:
            # Daemon "tick"
            msg = to_daemon.get()
            LOG.debug("Daemon has received the message %r", msg)
            if msg.message == "exit":
                keep_running = False
            else:
                LOG.debug(
                    "Message %r is currently not supported by the daemon", msg
                )
        except KeyboardInterrupt:
            LOG.debug("Keyboard interrupt")
            keep_running = False


def start_process(
    to_daemon: Optional["Queue[QueueMessage]"] = None,
    to_web: Optional["Queue[QueueMessage]"] = None,
) -> ProcessInfo:
    """
    Start the daemon process and return a ProcessInfo object. The ProcessInfo
    object contains references to the Queues used to communicate with the daemon
    process.
    """
    to_daemon = to_daemon or Queue()
    to_web = to_daemon or Queue()
    proc = Process(target=process, args=(to_daemon, to_web), daemon=True)
    proc.start()
    atexit.register(cleanup(proc, to_daemon))
    return ProcessInfo(to_daemon, to_web, proc)
