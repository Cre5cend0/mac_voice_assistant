from multiprocessing.pool import ThreadPool
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from time import sleep


def queue_not_empty(queue):
    status = queue.not_empty
    return status


class WorkerBox:
    def __init__(self, workers):
        self.max_workers = workers
        self.pool = ThreadPool(processes=self.max_workers)

    @staticmethod
    def trigger_background_worker(method, args=(), kwargs={}, name=None):
        daemon = Thread(target=method, args=args, kwargs=kwargs, daemon=True, name=name)
        daemon.start()

    def activate(self, queues, methods):
        while True:
            try:
                with ThreadPoolExecutor(max_workers=len(queues)) as exe:
                    triggers = exe.map(queue_not_empty, queues)

                for i, trigger in enumerate(triggers):
                    if trigger:
                        self.pool.apply_async(methods[i])
                sleep(0.2)
            except KeyboardInterrupt:
                break
