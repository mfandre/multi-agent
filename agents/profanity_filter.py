import json
import time

from database import Database
from queue_factory import QueueFactory

def profanity_filter_worker(db:Database):
    print("starting profanity_filter_worker")
    q_factory = QueueFactory()
    while True:
        output_queue = q_factory.get_queue("profanity_filter_output")
        input_queue = q_factory.get_queue("profanity_filter")
        print(f"running profanity_filter_worker. empty {input_queue.empty()} | size {input_queue.size}")
        if not input_queue.empty():
            try:
                print("processing profanity_filter_worker")
                message_q = input_queue.get()
                message, _ = db.get_message(message_q)
                if "profanity_checked" in message.get("processed", []):
                    continue
                message["result"] = message["text"].replace("badword", "****")
                message.setdefault("processed", []).append("profanity_checked")
                input_queue.ack(message_q)
                output_queue.put(message_q)
                db.update_message(message_q, message)
                print(f"end process agent profanity_filter_worker")
            except Exception as e:
                print(e)
        time.sleep(10)

if __name__ == "__main__":
    db = Database()
    profanity_filter_worker(db)