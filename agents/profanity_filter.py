import json
import time
from litequeue import LiteQueue

from database import Database

def profanity_filter_worker(db:Database):
    print("starting profanity_filter_worker")
    input_queue = LiteQueue("profanity_filter.db")
    output_queue = LiteQueue("profanity_output.db")
    while True:
        if not input_queue.empty():
            message_q = input_queue.pop()
            message = db.get_message(message_q.message_id)
            if "profanity_checked" in message.get("processed", []):
                continue
            message["result"] = message["text"].replace("badword", "****")
            message.setdefault("processed", []).append("profanity_checked")
            db.update_message(message_q.message_id, message)
            output_queue.put(message_q.message_id)
        time.sleep(1)

if __name__ == "__main__":
    db = Database()
    profanity_filter_worker(db)