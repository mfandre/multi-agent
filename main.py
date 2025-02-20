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
    
    queue_factory = QueueFactory()
    orchestrator = StateMachineOrchestrator(queue_factory, db)

    text = {"text": "This is a good day"}
    message_id = db.save_message(text)
    orchestrator.enqueue_initial_message(message_id)
    
    while True:
        for queue_name in orchestrator.get_queues():
            queue = queue_factory.get_queue(queue_name)
            if not queue.empty():
                message_id = queue.pop() #.get()
                print(message_id)
                orchestrator.process_message(queue_name, message_id.message_id)
        time.sleep(1)
    