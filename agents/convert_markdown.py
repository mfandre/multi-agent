import json
import time
from litequeue import LiteQueue
from database import Database

def convert_markdown_worker(db:Database):
    print("starting convert_markdown_worker")
    input_queue = LiteQueue("convert_markdown.db")
    output_queue = LiteQueue("markdown_output.db")
    while True:
        if not input_queue.empty():
            message_q = input_queue.pop()
            message, _ = db.get_message(message_q.message_id)
            text = message["text"]
            message["result"] = f"# {text}"
            db.update_message(message_q.message_id, message, "converted")
            output_queue.put(message_q.message_id)
        time.sleep(1)

if __name__ == "__main__":
    db = Database()
    convert_markdown_worker(db)