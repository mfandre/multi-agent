import json
import time
import markdown
from queue_manager.queue_factory import QueueFactory
import text_store
from config import queue_client

def markdown_agent():
    
    while True:
        queue_client = QueueFactory.get_queue("markdown_converter")
        messages = queue_client.receive_messages()
        for message in messages:
            if not message:
                continue

            text_id = message["text_id"]
            text = text_store.load_text(text_id)
            if text is None:
                continue
            
            markdown_text = markdown.markdown(text)
            new_text_id = text_store.save_text(markdown_text)

            queue_client = QueueFactory.get_queue("results")
            queue_client.send_message({"text_id": new_text_id, "output": None, "source_state" : "markdown_converter"})

        time.sleep(1)  # Evita consumo excessivo da fila

if __name__ == "__main__":
    markdown_agent()