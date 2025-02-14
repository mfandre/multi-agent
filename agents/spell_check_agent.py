import json
import time
from queue_manager.queue_factory import QueueFactory
import text_store

COMMON_MISTAKES = {
    "vc": "você",
    "pq": "porque",
    "tbm": "também",
    "tb": "também"
}

def correct_spelling(text):
    words = text.split()
    corrected_text = " ".join(COMMON_MISTAKES.get(word, word) for word in words)
    return corrected_text

def spellcheck_agent():
    while True:
        queue_client = QueueFactory.get_queue("spell_check")
        messages = queue_client.receive_messages()
        if not messages:
            continue

        for message in messages:
            text_id = message["text_id"]
            text = text_store.load_text(text_id)
            if text is None:
                continue

            corrected_text = correct_spelling(text)
            text_store.save_text(corrected_text,text_id)

            queue_client = QueueFactory.get_queue("results")
            queue_client.send_message({"text_id": text_id, "output": None, "source_state" : "spell_check"})
            
        time.sleep(1)

if __name__ == "__main__":
    spellcheck_agent()
