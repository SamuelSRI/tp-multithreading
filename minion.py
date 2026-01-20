import time

from task import Task
from queue_manager import QueueManager


class Minion:
    def __init__(self, host="127.0.0.1", port=50000, authkey=b"tp"):
        self.host = host
        self.port = port
        self.authkey = authkey

    def run(self):
        manager = QueueManager(address=(self.host, self.port), authkey=self.authkey)

        for _ in range(50):
            try:
                manager.connect()
                break
            except ConnectionRefusedError:
                time.sleep(0.1)
        else:
            raise RuntimeError("Impossible de se connecter au manager")

        task_queue = manager.task_queue()
        result_queue = manager.result_queue()

        while True:
            item = task_queue.get()
            if item is None:
                break

            task_id, size = item
            t = Task(identifier=task_id, size=size)
            t.work()

            result_queue.put((t.identifier, t.time))
