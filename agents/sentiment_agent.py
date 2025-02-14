import json
import time
from queue_manager.queue_factory import QueueFactory
import text_store
from config import queue_client

def analyze_sentiment(text):
    if "bom" in text or "feliz" in text:
        return "positive"
    elif "triste" in text or "ruim" in text:
        return "negative"
    return "neutral"

def sentiment_agent():
    while True:
        queue_client = QueueFactory.get_queue("sentiment_analysis")
        messages = queue_client.receive_messages()  # Lê da fila do agente
        if not messages:
            continue

        for message in messages:
            text_id = message["text_id"]
            text = text_store.load_text(text_id)
            if text is None:
                continue

            result = analyze_sentiment(text)
            text_store.save_text(result, text_id)  

            queue_client = QueueFactory.get_queue("results")
            queue_client.send_message({"text_id": text_id, "output": result, "source_state" : "sentiment_analysis"})  # Publica na fila de resultados
        time.sleep(1)

if __name__ == "__main__":
    sentiment_agent()