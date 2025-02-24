import json
import time
from database import Database
from queue_factory import QueueFactory

def sentiment_analysis_worker(db:Database):
    print("starting sentiment_analysis_worker")
    q_factory = QueueFactory()
    input_queue = q_factory.get_queue("sentiment_analysis")
    output_queue = q_factory.get_queue("sentiment_output")
    while True:
        print("running sentiment_analysis_worker")
        if not input_queue.empty():
            message_q = input_queue.pop()
            print(message_q)
            message, _ = db.get_message(message_q.data)
            print(message)
            message["sentiment"] = "positive" if "good" in message["text"] else "negative"
            message.setdefault("processed", []).append("sentiment_anlysed")
            print(message)
            input_queue.done(message_q.message_id)
            output_queue.put(message_q.data)
            db.update_message(message_q.data, message)
        time.sleep(10)

if __name__ == "__main__":
    db = Database()
    sentiment_analysis_worker(db)