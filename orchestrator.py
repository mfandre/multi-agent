import threading
import time
from transitions import Machine

from database import Database
from queue_factory import QueueFactory

# Orchestrator
class StateMachineOrchestrator:
    transitions = [
        {"trigger": "process_profanity", "source": "start", "dest": "profanity_checked", "queue": "sentiment_analysis"},
        {"trigger": "process_sentiment", "source": "profanity_checked", "dest": "converted", "queue": "convert_markdown", "conditions": "is_positive"},
        {"trigger": "process_sentiment", "source": "profanity_checked", "dest": "summarized", "queue": "summarize_text", "conditions": "is_negative"},
        {"trigger": "process_markdown", "source": "converted", "dest": "done"},
        {"trigger": "process_summary", "source": "summarized", "dest": "done"}
    ]

    def __init__(self, queue_factory:QueueFactory, database:Database):
        self.queue_factory = queue_factory
        self.database = database
        self.machine = Machine(model=self, states=[t["dest"] for t in self.transitions] + ["start"], initial="start")
        for transition in self.transitions:
            self.machine.add_transition(
                transition["trigger"], transition["source"], transition["dest"]
            )

    def get_queues(self) -> set:
        monitored_queues = set()
        for transition in self.transitions:
            queue_name = transition.get("queue")
            if queue_name and queue_name not in monitored_queues:
                monitored_queues.add(queue_name)
        return monitored_queues

    def is_positive(self, message):
        return message.get("sentiment") == 'positive'

    def is_negative(self, message):
        return message.get("sentiment") == 'negative'

    def process_message(self, queue_name, message_id):
        message, state = self.database.get_message(message_id)
        if not message:
            return

        for transition in self.transitions:
            if transition["source"] == state and queue_name.endswith("_output"):
                next_state = transition["dest"]
                queue = transition.get("queue")
                
                if "conditions" in transition and not getattr(self, transition["conditions"])(message):
                    continue
                
                if queue:
                    self.queue_factory.get_queue(queue).put(message_id)
                else:
                    print("Final Output:", message["result"])
                
                self.database.update_message(message_id, message, next_state)
                break

    def start_processing(self, text):
        message_id = self.database.save_message(text)
        self.queue_factory.get_queue("profanity_filter").put(message_id)
        self.monitor_queues()

    def monitor_queues(self):
        monitored_queues = set()
        while True:
            for transition in self.transitions:
                queue_name = transition.get("queue")
                if queue_name and queue_name not in monitored_queues:
                    monitored_queues.add(queue_name)
                    threading.Thread(target=self.monitor_queue, args=(queue_name,), daemon=True).start()
            time.sleep(1)

    def monitor_queue(self, queue_name):
        queue = self.queue_factory.get_queue(queue_name)
        while True:
            print(f"{queue_name} empty {queue.empty()}")
            print(f"{queue_name} size {queue.qsize()}")
            if not queue.empty():
                message_id = queue.pop()
                self.process_message(queue_name, message_id)
            time.sleep(0.1)