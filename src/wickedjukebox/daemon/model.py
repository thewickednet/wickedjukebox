from dataclasses import dataclass
from multiprocessing import Process, Queue


@dataclass
class QueueMessage:
    message: str


@dataclass
class ProcessInfo:
    queue: "Queue[QueueMessage]"
    process: Process
