import os
# from litequeue import LiteQueue
from persistqueue.sqlackqueue import SQLiteAckQueue

class QueueFactory:
    def __init__(self, base_path="dbs"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
        self.queues = {}

    def get_queue(self, name) -> SQLiteAckQueue:
        # if name not in self.queues:
        #     self.queues[name] = SQLiteAckQueue(os.path.join(self.base_path, name), multithreading=True, auto_commit=True)
        # return self.queues[name]
        return SQLiteAckQueue(os.path.join(self.base_path, name), multithreading=True, auto_commit=True)

