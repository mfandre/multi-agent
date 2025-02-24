import json
import time
from litequeue import LiteQueue
from database import Database
from queue_factory import QueueFactory

def summarize_text_worker(db:Database):
    print("starting summarize_text_worker")
    q_factory = QueueFactory()
    input_queue = q_factory.get_queue("summarize_text")
    output_queue = q_factory.get_queue("summarize_output")
    while True:
        print("running summarize_text_worker")
        if not input_queue.empty():
            message_q = input_queue.pop()
            message, _ = db.get_message(message_q.data)
            message["result"] = message["text"].split()[0]
            message.setdefault("processed", []).append("summarized")
            input_queue.done(message_q.message_id)
            output_queue.put(message_q.data)
            db.update_message(message_q.data, message)
        time.sleep(10)

if __name__ == "__main__":
    db = Database()
    summarize_text_worker(db)