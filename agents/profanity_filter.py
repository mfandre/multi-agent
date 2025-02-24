import json
import time

from database import Database
from queue_factory import QueueFactory

def profanity_filter_worker(db:Database):
    print("starting profanity_filter_worker")
    q_factory = QueueFactory()
    input_queue = q_factory.get_queue("profanity_filter")
    output_queue = q_factory.get_queue("profanity_filter_output")
    while True:
        if not input_queue.empty():
            print(f"agent profanity_filter_worker")
            message_q = input_queue.pop()
            message, _ = db.get_message(message_q.data)
            if "profanity_checked" in message.get("processed", []):
                continue
            message["result"] = message["text"].replace("badword", "****")
            message.setdefault("processed", []).append("profanity_checked")
            db.update_message(message_q.data, message, None)
            output_queue.put(message_q.data)
            input_queue.done(message_q.message_id)
            print(f"end process agent profanity_filter_worker")
        time.sleep(1)

if __name__ == "__main__":
    db = Database()
    profanity_filter_worker(db)