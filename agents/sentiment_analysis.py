import json
import time
from database import Database
from queue_factory import QueueFactory
from log_wrapper import app_log

def sentiment_analysis_worker(db:Database):
    app_log.debug("starting sentiment_analysis_worker")
    q_factory = QueueFactory()
    
    while True:
        input_queue = q_factory.get_queue("sentiment_analysis")
        output_queue = q_factory.get_queue("sentiment_analysis_output")
        app_log.debug(f"running sentiment_analysis_worker. empty {input_queue.empty()} | size {input_queue.size}")
        if not input_queue.empty():
            message_q = input_queue.get()
            app_log.debug(message_q)
            message, _ = db.get_message(message_q)
            app_log.debug(message)
            message["sentiment"] = "positive" if "good" in message["text"] else "negative"
            message.setdefault("processed", []).append("sentiment_anlysed")
            app_log.debug(message)
            input_queue.ack(message_q)
            output_queue.put(message_q)
            db.update_message_without_updating_state(message_q, message)
        time.sleep(10)

if __name__ == "__main__":
    db = Database()
    sentiment_analysis_worker(db)