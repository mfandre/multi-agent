import json
import time

from database import Database
from queue_factory import QueueFactory
from log_wrapper import app_log

def profanity_filter_worker(db:Database):
    app_log.debug("starting profanity_filter_worker")
    q_factory = QueueFactory()
    while True:
        output_queue = q_factory.get_queue("profanity_filter_output")
        input_queue = q_factory.get_queue("profanity_filter")
        app_log.debug(f"running profanity_filter_worker. empty {input_queue.empty()} | size {input_queue.size}")
        if not input_queue.empty():
            try:
                app_log.debug("processing profanity_filter_worker")
                message_q = input_queue.get()
                message, _ = db.get_message(message_q)
                message["result"] = message["text"].replace("badword", "****")
                message.setdefault("processed", []).append("profanity_checked")
                input_queue.ack(message_q)
                output_queue.put(message_q)
                db.update_message_without_updating_state(message_q, message)
                app_log.debug(f"end process agent profanity_filter_worker")
            except Exception as e:
                app_log.debug(e)
        time.sleep(10)

if __name__ == "__main__":
    db = Database()
    profanity_filter_worker(db)