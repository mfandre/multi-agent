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
        print("running convert_markdown_worker")
        if not input_queue.empty():
            message_q = input_queue.pop()
            message, _ = db.get_message(message_q.data)
            text = message["text"]
            message["result"] = f"# {text}"
            message.setdefault("processed", []).append("markdowned")
            input_queue.done(message_q.message_id)
            output_queue.put(message_q.data)
            db.update_message(message_q.data, message)
        time.sleep(10)

if __name__ == "__main__":
    db = Database()
    convert_markdown_worker(db)