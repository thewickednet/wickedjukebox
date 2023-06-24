import atexit
from multiprocessing import Process, Queue
from os.path import exists
from time import sleep

from wickedjukebox.daemon.model import ProcessInfo, QueueMessage


def cleanup(process: Process):
    """
    Generate a cleanup function for the process.
    """

    def callback():
        print("Cleaning up")
        try:
            process.join()
        except KeyboardInterrupt:
            print("Keyboard interrupt")
        print("Cleaned up")

    return callback


def process(
    to_daemon: "Queue[QueueMessage]", to_web: "Queue[QueueMessage]"
) -> None:
    """
    A dummy implementation of the daemon process.
    """
    while True:
        try:
            while True:
                if exists("/tmp/foo"):
                    with open("/tmp/foo") as f:
                        msg = f.read()
                        to_web.put(QueueMessage(msg))
                sleep(1)
            # item = to_daemon.get()
            # updated = QueueMessage(f"Updated: {item.message}")
        except KeyboardInterrupt:
            print("Keyboard interrupt")
            break


def start_process() -> ProcessInfo:
    """
    Start the daemon process and return a ProcessInfo object. The ProcessInfo
    object contains references to the Queues used to communicate with the daemon
    process.
    """
    to_daemon: "Queue[QueueMessage]" = Queue()
    to_web: "Queue[QueueMessage]" = Queue()
    p = Process(target=process, args=(to_daemon, to_web))
    p.start()
    atexit.register(cleanup(p))
    return ProcessInfo(to_daemon, to_web)
