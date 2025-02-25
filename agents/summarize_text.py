import json
import time
from litequeue import LiteQueue
from database import Database
from queue_factory import QueueFactory
from log_wrapper import app_log

def summarize_text_worker(db:Database):
    app_log.debug("starting summarize_text_worker")
    q_factory = QueueFactory()
    
    while True:
        input_queue = q_factory.get_queue("summarize_text")
        output_queue = q_factory.get_queue("summarize_text_output")
        app_log.debug(f"running sentiment_analysis_worker. empty {input_queue.empty()} | size {input_queue.size}")
        if not input_queue.empty():
            message_q = input_queue.get()
            message, _ = db.get_message(message_q)
            if "result" in message:
                text = message["result"]
            else:
                text = message["text"]
            message["result"] = text.split()[0]
            message.setdefault("processed", []).append("summarized")
            input_queue.ack(message_q)
            output_queue.put(message_q)
            db.update_message_without_updating_state(message_q, message)
        time.sleep(10)

if __name__ == "__main__":
    db = Database()
    summarize_text_worker(db)