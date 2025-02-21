import os
from litequeue import LiteQueue

class QueueFactory:
    def get_queue(self, queue_name):
        db_path = os.path.join("dbs", f"{queue_name}.db")
        return LiteQueue(db_path)