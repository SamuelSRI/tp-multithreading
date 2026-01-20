from multiprocessing.managers import BaseManager
from queue import Queue

_task_queue = Queue()
_result_queue = Queue()


def get_task_queue():
    return _task_queue


def get_result_queue():
    return _result_queue


class QueueManager(BaseManager):
    pass


QueueManager.register("task_queue", callable=get_task_queue)
QueueManager.register("result_queue", callable=get_result_queue)
