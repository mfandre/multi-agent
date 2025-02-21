import json
import time
from queue_factory import QueueFactory
from database import Database

def convert_markdown_worker(db:Database):
    print("starting convert_markdown_worker")
    q_factory = QueueFactory()
    input_queue = q_factory.get_queue("convert_markdown")
    output_queue = q_factory.get_queue("markdown_output")
    while True:
        if not input_queue.empty():
            message_q = input_queue.pop()
            message, _ = db.get_message(message_q.data)
            text = message["text"]
            message["result"] = f"# {text}"
            db.update_message(message_q.data, message, None)
            output_queue.put(message_q.data)
            input_queue.done(message_q.message_id)
        time.sleep(1)

if __name__ == "__main__":
    db = Database()
    convert_markdown_worker(db)