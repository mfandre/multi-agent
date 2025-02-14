import json
import time
import text_store
from queue_manager.queue_factory import QueueFactory
from config import FORBIDDEN_WORDS

def filter_agent():
    while True:
        queue_client = QueueFactory.get_queue("filter_text")
        messages = queue_client.receive_messages()
        if not messages:
            continue

        for message in messages:
            text_id = message["text_id"]
            text = text_store.load_text(text_id)

            for word in FORBIDDEN_WORDS:
                text = text.replace(word, "*" * len(word))  # Censura palavras proibidas
            new_text_id = text_store.save_text(text, text_id)

            queue_client = QueueFactory.get_queue("results")
            queue_client.send_message({"text_id": new_text_id, "output": None, "source_state" : "filter_text"})

        time.sleep(1)  # Evita consumo excessivo da fila

if __name__ == "__main__":
    filter_agent()