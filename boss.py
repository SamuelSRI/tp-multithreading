import multiprocessing as mp

from queue_manager import QueueManager
from minion import Minion


class Boss:
    def __init__(self, host="127.0.0.1", port=50000, authkey=b"tp"):
        self.host = host
        self.port = port
        self.authkey = authkey

    def run(self, n_tasks=10, n_minions=4, task_size=200):
        # Démarre le manager proprement (shutdown possible)
        manager = QueueManager(address=(self.host, self.port), authkey=self.authkey)
        manager.start()

        task_queue = manager.task_queue()
        result_queue = manager.result_queue()

        # Lance les minions (process)
        procs = []
        for _ in range(n_minions):
            p = mp.Process(target=Minion(self.host, self.port, self.authkey).run)
            p.start()
            procs.append(p)

        # Envoie les tâches
        for i in range(n_tasks):
            task_queue.put((i, task_size))

        # Stop minions
        for _ in range(n_minions):
            task_queue.put(None)

        # Collect results
        results = [result_queue.get() for _ in range(n_tasks)]
        results.sort(key=lambda x: x[0])

        print("Results (id, time):")
        for r in results:
            print(r)

        for p in procs:
            p.join()

        # Arrêt propre => pas de "leaked semaphores"
        manager.shutdown()


if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)
    Boss().run(n_tasks=10, n_minions=4, task_size=200)
