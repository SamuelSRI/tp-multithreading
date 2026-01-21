import argparse
import multiprocessing as mp
import subprocess
import sys
import time

from queue_manager import QueueManager
from task import Task
from manager import QueueClient


def start_manager(host: str, port: int, authkey: bytes) -> QueueManager:
    mp.set_start_method("spawn", force=True)
    manager = QueueManager(address=(host, port), authkey=authkey)
    manager.start()
    return manager


def produce_tasks(n_tasks: int, size: int):
    c = QueueClient()
    for i in range(n_tasks):
        c.task_queue.put(Task(identifier=i, size=size))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    serve = sub.add_parser("serve", help="Start QueueManager + run proxy.py (HTTP)")
    serve.add_argument("--manager-host", default="127.0.0.1")
    serve.add_argument("--manager-port", type=int, default=50000)
    serve.add_argument("--authkey", default="tp")
    serve.add_argument("--proxy-port", type=int, default=8000)

    prod = sub.add_parser("produce", help="Enqueue Task objects into task_queue")
    prod.add_argument("-n", "--n-tasks", type=int, default=20)
    prod.add_argument("--size", type=int, default=200)

    args = parser.parse_args()

    if args.cmd == "serve":
        authkey = args.authkey.encode()
        manager = start_manager(args.manager_host, args.manager_port, authkey)
        print(f"QueueManager started on {args.manager_host}:{args.manager_port}")

        proxy_proc = subprocess.Popen([sys.executable, "proxy.py"])
        print(f"Proxy started on http://127.0.0.1:{args.proxy_port} (proxy.py)")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            proxy_proc.terminate()
            proxy_proc.wait(timeout=5)
            manager.shutdown()

    elif args.cmd == "produce":
        produce_tasks(args.n_tasks, args.size)
        print(f"Enqueued {args.n_tasks} tasks (size={args.size}).")


if __name__ == "__main__":
    main()
