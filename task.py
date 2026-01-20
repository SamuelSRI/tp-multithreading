import time
import json
import numpy as np


class Task:
    def __init__(self, identifier=0, size=None):
        self.identifier = identifier
        self.size = size or np.random.randint(300, 3_000)
        self.a = np.random.rand(self.size, self.size)
        self.b = np.random.rand(self.size)
        self.x = np.zeros((self.size))
        self.time = 0

    def work(self):
        start = time.perf_counter()
        self.x = np.linalg.solve(self.a, self.b)
        self.time = time.perf_counter() - start

    def to_json(self) -> str:
        data = {
            "identifier": self.identifier,
            "size": self.size,
            "a": self.a.tolist(),
            "b": self.b.tolist(),
            "x": self.x.tolist(),
            "time": self.time,
        }
        return json.dumps(data)

    @staticmethod
    def from_json(text: str) -> "Task":
        data = json.loads(text)

        t = Task(identifier=data["identifier"], size=data["size"])
        t.a = np.array(data["a"])
        t.b = np.array(data["b"])
        t.x = np.array(data["x"])
        t.time = data["time"]

        return t

    def __eq__(self, other: "Task") -> bool:
        if not isinstance(other, Task):
            return False

        return (
            self.identifier == other.identifier
            and self.size == other.size
            and np.allclose(self.a, other.a)
            and np.allclose(self.b, other.b)
            and np.allclose(self.x, other.x)
            and abs(self.time - other.time) < 1e-9
        )
