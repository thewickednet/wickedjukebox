import atexit
import logging
from multiprocessing import Process, Queue
from queue import Empty
from time import sleep

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
            msg = to_daemon.get(timeout=10)
            LOG.error("Daemon has received the message %r", msg)
            if msg.message == "exit":
                keep_running = False
            else:
                LOG.debug(
                    "Message %r is currently not supported by the daemon", msg
                )
        except Empty:
            LOG.debug("No message on queue")
            sleep(1)
        except KeyboardInterrupt:
            LOG.debug("Keyboard interrupt")
            keep_running = False


def start_process() -> ProcessInfo:
    """
    Start the daemon process and return a ProcessInfo object. The ProcessInfo
    object contains references to the Queues used to communicate with the daemon
    process.
    """
    to_daemon: "Queue[QueueMessage]" = Queue()
    to_web: "Queue[QueueMessage]" = Queue()
    p = Process(target=process, args=(to_daemon, to_web), daemon=True)
    p.start()
    atexit.register(cleanup(p, to_daemon))
    return ProcessInfo(to_daemon, to_web)
