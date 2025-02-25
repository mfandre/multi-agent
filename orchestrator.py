import threading
import time
from transitions import Machine
from transitions.extensions import GraphMachine

from database import Database
from queue_factory import QueueFactory

from log_wrapper import app_log

# Orchestrator
class StateMachineOrchestrator:
    transitions = [
        {"trigger": "process_profanity_filter", "source": "start", "dest": "profanity_checked"},
        {"trigger": "process_sentiment_analysis", "source": "profanity_checked", "dest": "converted", "conditions": "is_positive"},
        {"trigger": "process_sentiment_analysis", "source": "profanity_checked", "dest": "summarized", "conditions": "is_negative"},
        {"trigger": "process_convert_markdown", "source": "converted", "dest": "done"},
        {"trigger": "process_summarize_text", "source": "summarized", "dest": "done"}
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

    def process_profanity_filter(self, message_id):
        self.process_transition(message_id, "sentiment_analysis")

    def process_sentiment_analysis(self, message_id):
        message, _ = self.database.get_message(message_id)
        if self.is_positive(message):
            self.process_transition(message_id, "convert_markdown")
        else:
            self.process_transition(message_id, "summarize_text")

    def process_convert_markdown(self, message_id):
        self.process_transition(message_id, "done")

    def process_summarize_text(self, message_id):
        self.process_transition(message_id, "done")

    def process_transition(self, message_id, next_queue):
        message, state = self.database.get_message(message_id)
        if not message:
            app_log.error(f"Message {message_id} not found in database")
            return

        for transition in self.transitions:
            if transition["source"] == state:
                next_state = transition["dest"]
                self.database.update_message(message_id, message, next_state)
                self.queue_factory.get_queue(next_queue).put(message_id)
                app_log.debug(f"Message {message_id} sent to {next_queue}")
                break


    def start_processing(self, text):
        message_id = self.database.save_message(text)
        q = self.queue_factory.get_queue("profanity_filter")
        q.put(message_id)
        # q.task_done()
        app_log.debug(f"Message {message_id} added to 'profanity_filter'. Size = {q.size}")
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
            app_log.debug(f"Starting thread for queue: {queue_name}")
            threading.Thread(target=self.monitor_queue, args=(queue_name,), daemon=True).start()
            # time.sleep(1)

    def monitor_queue(self, queue_name):
        while True:
            queue = self.queue_factory.get_queue(queue_name)
            app_log.debug(f"Orchestrator - {queue_name} qsize {queue.size}")
            if not queue.empty():
                message = queue.get()
                try:
                    app_log.debug(f"Orchestrator - Processing message {message} from {queue_name}")
                    trigger = "process_" + queue_name.replace("_output", "")
                    trigger_method = getattr(self, trigger, None)
                    if trigger_method:
                        trigger_method(message)
                        queue.ack(message)
                        app_log.debug(f"Orchestrator - ACK message {message} from {queue_name}")
                except Exception as e:
                    app_log.error(f"Orchestrator - NACK processing message {message} from {queue_name}",exc_info=True)
                    queue.nack(message)
            time.sleep(10)

    def draw_state_machine(self):
        self.machine.get_graph().draw('state_diagram.png', prog='dot')