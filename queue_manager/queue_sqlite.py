import json
from queue_manager.queue_manager import QueueManager
from litequeue import LiteQueue, Message
from config import SQLITE_QUEUE_PATH

class SQLiteQueue(QueueManager):
    queue:LiteQueue = None
    def __init__(self, topic:str):
        self.queue = LiteQueue(SQLITE_QUEUE_PATH, queue_name=topic)

    def send_message(self, message: dict):
        self.queue.put(json.dumps(message))

    def receive_messages(self):
        return [self.queue.pop()]

    def delete_message(self, message_id):
        self.queue.done(message_id)