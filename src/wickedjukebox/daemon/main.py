import atexit
from multiprocessing import Process, Queue

from wickedjukebox.daemon.model import ProcessInfo, QueueMessage


def cleanup(process: Process):
    def callback():
        print("Cleaning up")
        try:
            process.join()
        except KeyboardInterrupt:
            print("Keyboard interrupt")
        print("Cleaned up")

    return callback


def process(queue: "Queue[QueueMessage]") -> None:
    print("Starting process")
    while True:
        print("Waiting for queue")
        try:
            item = queue.get()
        except KeyboardInterrupt:
            print("Keyboard interrupt")
            break
        print(f"Got item from queue: {item}")


def start_process() -> ProcessInfo:
    queue: "Queue[QueueMessage]" = Queue()
    p = Process(target=process, args=(queue,))
    p.start()
    print("running")
    atexit.register(cleanup(p))
    return ProcessInfo(queue=queue, process=p)
