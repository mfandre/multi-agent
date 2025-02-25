import threading
import time
from transitions import Machine
from transitions.extensions import GraphMachine

from database import Database
from queue_factory import QueueFactory

# Orchestrator
class StateMachineOrchestrator:
    transitions = [
        {"trigger": "process_profanity", "source": "start", "dest": "profanity_checked"},
        {"trigger": "process_sentiment", "source": "profanity_checked", "dest": "converted", "conditions": "is_positive"},
        {"trigger": "process_sentiment", "source": "profanity_checked", "dest": "summarized", "conditions": "is_negative"},
        {"trigger": "process_markdown", "source": "converted", "dest": "done"},
        {"trigger": "process_summary", "source": "summarized", "dest": "done"}
    ]

    def __init__(self, queue_factory:QueueFactory, database:Database):
        self.queue_factory = queue_factory
        self.database = database
        self.machine = GraphMachine(model=self, states=[t["dest"] for t in self.transitions] + ["start"], initial="start")
        for transition in self.transitions:
            self.machine.add_transition(
                transition["trigger"], transition["source"], transition["dest"]
            )

    def is_positive(self, message):
        return message.get("sentiment") == "positive"

    def is_negative(self, message):
        return message.get("sentiment") == "negative"

    def process_profanity(self, message_id):
        self.process_transition(message_id, "profanity_filter_output")

    def process_sentiment(self, message_id):
        message, _ = self.database.get_message(message_id)
        if self.is_positive(message):
            self.process_transition(message_id, "convert_markdown_output")
        else:
            self.process_transition(message_id, "summarize_text_output")

    def process_markdown(self, message_id):
        self.process_transition(message_id, "done")

    def process_summary(self, message_id):
        self.process_transition(message_id, "done")

    def process_transition(self, message_id, next_queue):
        message, state = self.database.get_message(message_id)
        if not message:
            print(f"[ERROR] Message {message_id} not found in database")
            return

        for transition in self.transitions:
            if transition["source"] == state:
                next_state = transition["dest"]
                self.database.update_message(message_id, message, next_state)
                self.queue_factory.get_queue(next_queue).put(message_id)
                print(f"[DEBUG] Message {message_id} sent to {next_queue}")
                break


    def start_processing(self, text):
        message_id = self.database.save_message(text)
        self.queue_factory.get_queue("profanity_filter").put(message_id)
        self.monitor_queues()

    def get_queues(self) -> set:
        queues = ["profanity_filter", "convert_markdown", "sentiment_analysis", "summarize_text"]
        
        monitored_queues = set()
        for q in queues:
            # monitored_queues.add(q)  # Fila de entrada
            monitored_queues.add(f"{q}_output")  # Fila de saída

        return monitored_queues
    
    def monitor_queues(self):
        for queue_name in self.get_queues():
            print(f"[DEBUG] Starting thread for queue: {queue_name}")
            threading.Thread(target=self.monitor_queue, args=(queue_name,), daemon=True).start()
            # time.sleep(1)

    def monitor_queue(self, queue_name):
        queue = self.queue_factory.get_queue(queue_name)
        while True:
            print(f"[DEBUG] Orchestrator - {queue_name} qsize {queue.size}")
            if not queue.empty():
                message = queue.get()
                print(f"Processing message {message} from {queue_name}")
                trigger_method = getattr(self, f"process_{queue_name}", None)
                if trigger_method:
                    trigger_method(message)
            time.sleep(10)

    def draw_state_machine(self):
        self.machine.get_graph().draw('state_diagram.png', prog='dot')