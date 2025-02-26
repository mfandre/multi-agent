import json
import time
from queue_factory import QueueFactory
from database import Database
from log_wrapper import app_log

def convert_markdown_worker(db:Database):
    app_log.debug("starting convert_markdown_worker")
    q_factory = QueueFactory()
    while True:
        input_queue = q_factory.get_queue("convert_markdown")
        output_queue = q_factory.get_queue("convert_markdown_output")
        app_log.debug(f"running convert_markdown_worker. empty {input_queue.empty()} | size {input_queue.size}")
        if not input_queue.empty():
            message_q = input_queue.get()
            message, _ = db.get_message(message_q)
            if "result" in message:
                text = message["result"]
            else:
                text = message["text"]
            message["result"] = f"# {text}"
            message.setdefault("processed", []).append("markdowned")
            input_queue.ack(message_q)
            output_queue.put(message_q)
            db.update_message_without_updating_state(message_q, message)
        time.sleep(10)

if __name__ == "__main__":
    db = Database()
    convert_markdown_worker(db)