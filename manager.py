import time
from queue_manager import QueueManager


class QueueClient:
    def __init__(self, host="127.0.0.1", port=50000, authkey=b"tp"):
        self.host = host
        self.port = port
        self.authkey = authkey

        self.manager = QueueManager(
            address=(self.host, self.port), authkey=self.authkey
        )
        self.task_queue = None
        self.result_queue = None

        self.connect()

    def connect(self, retries: int = 50, delay: float = 0.1):
        last_err = None
        for _ in range(retries):
            try:
                self.manager.connect()
                self.task_queue = self.manager.task_queue()
                self.result_queue = self.manager.result_queue()
                return
            except ConnectionRefusedError as e:
                last_err = e
                time.sleep(delay)

        raise last_err
