from collections import deque


class BuildQueueService:
    def __init__(self) -> None:
        self.queue: deque[int] = deque()

    def enqueue(self, job_id: int) -> None:
        self.queue.append(job_id)

    def dequeue(self) -> int | None:
        return self.queue.popleft() if self.queue else None
