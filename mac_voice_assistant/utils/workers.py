from multiprocessing.pool import ThreadPool
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Thread
from time import sleep


class WorkerBox:
    def __init__(self, workers):
        self.pool = ThreadPoolExecutor(max_workers=workers)
        self.lock = Lock()

    def queue_not_empty(self, queue):
        with self.lock:
            status = queue.not_empty
        return status

    def trigger_background_worker(self, method, *args, **kwargs):
        with self.pool as exe:
            result = exe.submit(method, *args, **kwargs)
        return result

    def trigger_pool_workers(self, method, *iterables):
        with self.pool as exe:
            result = exe.map(method, *iterables)
        return result

    def get_queue_status(self, queues):
        try:
            response_list = []
            with self.pool as exe:
                triggers = exe.map(self.queue_not_empty, queues)
                for trigger in as_completed(triggers):
                    return_value = trigger.result()
                    response_list.append(return_value[0])
            return response_list
        except Exception as error:
            raise Exception(str(error))

    # def activate(self, queues, methods):
    #     while True:
    #         try:
    #             with self.pool as exe:
    #                 triggers = exe.map(queue_not_empty, queues)
    #                 my_list = triggers[0].result()
    #
    #             for i, trigger in enumerate(triggers):
    #                 if trigger:
    #                     self.pool.apply_async(methods[i])
    #             sleep(0.2)
    #         except KeyboardInterrupt:
    #             break
