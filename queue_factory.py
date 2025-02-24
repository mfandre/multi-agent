import os
from litequeue import LiteQueue
from persistqueue import Queue

class QueueFactory:
    def __init__(self):
        self.queues = {}

    def get_queue(self, queue_name):
        db_path = os.path.join("dbs", f"{queue_name}.db")
        return LiteQueue(db_path)
    
