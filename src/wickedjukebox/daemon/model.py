import json
from dataclasses import dataclass
from datetime import datetime
from multiprocessing import Process, Queue


@dataclass
class QueueMessage:
    """
    The model used for messages which are sent between the web and daemon process.
    """

    message: str

    def to_json(self) -> str:
        now = datetime.now().isoformat()
        return json.dumps({"now": now, "message": self.message})


@dataclass
class ProcessInfo:
    """
    Queue information for the daemon process.
    """

    to_daemon: "Queue[QueueMessage]"
    to_web: "Queue[QueueMessage]"
    process: Process
