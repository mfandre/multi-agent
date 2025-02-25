import threading
import time

from agents.convert_markdown import convert_markdown_worker
from agents.profanity_filter import profanity_filter_worker
from agents.sentiment_analysis import sentiment_analysis_worker
from agents.summarize_text import summarize_text_worker
from database import Database
from orchestrator import StateMachineOrchestrator
from queue_factory import QueueFactory

if __name__ == "__main__":
    db = Database() 
    threading.Thread(target=convert_markdown_worker, daemon=True, args=[db]).start()
    threading.Thread(target=profanity_filter_worker, daemon=True, args=[db]).start()
    threading.Thread(target=sentiment_analysis_worker, daemon=True, args=[db]).start()
    threading.Thread(target=summarize_text_worker, daemon=True, args=[db]).start()
    
    # wait to create DBs
    time.sleep(5)

    queue_factory = QueueFactory()
    orchestrator = StateMachineOrchestrator(queue_factory, db)
    # orchestrator.draw_state_machine()
    
    text = {"text": "This is a good day"}
    orchestrator.start_processing(text)
    while True:
        time.sleep(1)
    