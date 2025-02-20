import json
import time
from litequeue import LiteQueue
from database import Database

def summarize_text_worker(db:Database):
    print("starting summarize_text_worker")
    input_queue = LiteQueue("summarize_text.db")
    output_queue = LiteQueue("summarize_output.db")
    while True:
        if not input_queue.empty():
            message_q = input_queue.pop()
            message, _ = db.get_message(message_q.message_id)
            message["result"] = message["text"].split()[0]
            db.update_message(message_q.message_id, message, "summarized")
            output_queue.put(message_q.message_id)
        time.sleep(1)

if __name__ == "__main__":
    db = Database()
    summarize_text_worker(db)