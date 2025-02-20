from litequeue import LiteQueue

class QueueFactory:
    def get_queue(self, queue_name):
        return LiteQueue(f"{queue_name}.db")