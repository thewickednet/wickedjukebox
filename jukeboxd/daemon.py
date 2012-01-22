from multiprocessing import Process, Queue
from Queue import Empty
import logging

LOG = logging.getLogger(__name__)
MSG_STOP = "stop"
PROC = None

def daemond(queue):
    from time import sleep
    while True:
        print "."
        sleep(1)
        try:
            msg = queue.get_nowait()
            if msg == MSG_STOP:
                break
            else:
                LOG.warning("Unsupported messgage on the queue")
        except Empty:
            pass

def run():
    global PROC
    if PROC:
        raise IOError("Another process is already running!")
    queue = Queue()
    PROC = Process(target = daemond, args=(queue,))
    PROC.start()
    return queue

def stop(queue):
    global PROC
    queue.put(MSG_STOP)
    if PROC:
        PROC.join()
        PROC = None
