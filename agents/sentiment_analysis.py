import json
import time
from litequeue import LiteQueue
from database import Database

def sentiment_analysis_worker(db:Database):
    print("starting sentiment_analysis_worker")
    input_queue = LiteQueue("sentiment_analysis.db")
    output_queue = LiteQueue("sentiment_output.db")
    while True:
        print(f"sentiment_analysis_worker qsize => {input_queue.qsize()}")
        print(f"sentiment_analysis_worker empty => {input_queue.empty()}")
        if not input_queue.empty():
            message_q = input_queue.pop()
            print(message_q)
            message, _ = db.get_message(message_q.message_id)
            message["sentiment"] = "positive" if "good" in message["text"] else "negative"
            print(message)
            db.update_message(message_q.message_id, message, "analyzed")
            output_queue.put(message_q.message_id)
        time.sleep(1)

if __name__ == "__main__":
    db = Database()
    sentiment_analysis_worker(db)