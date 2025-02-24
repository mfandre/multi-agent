import threading
import time
from transitions import Machine
from transitions.extensions import GraphMachine

from database import Database
from queue_factory import QueueFactory

# Orchestrator
class StateMachineOrchestrator:
    transitions = [
        {"trigger": "process_profanity", "source": "start", "dest": "profanity_checked", "queue": "profanity_filter"},
        {"trigger": "process_sentiment", "source": "profanity_checked", "dest": "converted", "queue": "convert_markdown", "conditions": "is_positive"},
        {"trigger": "process_sentiment", "source": "profanity_checked", "dest": "summarized", "queue": "summarize_text", "conditions": "is_negative"},
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

    def get_queues(self) -> set:
        monitored_queues = set()
        
        for transition in self.transitions:
            queue_name = transition.get("queue")
            if queue_name:
                monitored_queues.add(queue_name)  # Fila de entrada
                monitored_queues.add(f"{queue_name}_output")  # Fila de saída

        return monitored_queues

    def is_positive(self, message):
        return message.get("sentiment") == 'positive'

    def is_negative(self, message):
        return message.get("sentiment") == 'negative'

    def process_message(self, queue_name, message_id):
        message, state = self.database.get_message(message_id)
        
        print(f"[DEBUG] Processing message {message_id} from {queue_name}")
        print(f"[DEBUG] Current state: {state}, Message: {message}")

        if not message:
            print(f"[ERROR] Message {message_id} not found in database")
            return

        for transition in self.transitions:
            if transition["source"] == state and queue_name.endswith("_output"):
                next_state = transition["dest"]
                next_queue = transition.get("queue")

                print(f"[DEBUG] Transitioning {message_id} from {state} -> {next_state}, next queue: {next_queue}")

                # Verifica condição antes de prosseguir
                if "conditions" in transition and not getattr(self, transition["conditions"])(message):
                    print(f"[DEBUG] Condition {transition['conditions']} not met for message {message_id}")
                    continue

                # Atualiza estado no banco de dados
                self.database.update_message(message_id, message, next_state)

                # Envia para a próxima fila, se houver um próximo estágio
                if next_queue:
                    self.queue_factory.get_queue(next_queue).put(message_id)
                    print(f"[DEBUG] Message {message_id} sent to {next_queue}")
                else:
                    print(f"[INFO] Final Output: {message.get('result', '')}")

                break

    def start_processing(self, text):
        message_id = self.database.save_message(text)
        self.queue_factory.get_queue("profanity_filter").put(message_id)
        self.monitor_queues()

    def monitor_queues(self):
        for queue_name in self.get_queues():
            print(f"[DEBUG] Starting thread for queue: {queue_name}")
            threading.Thread(target=self.monitor_queue, args=(queue_name,), daemon=True).start()
            # time.sleep(1)

    def monitor_queue(self, queue_name):
        queue = self.queue_factory.get_queue(queue_name)
        while True:
            if not queue.empty():
                message = queue.pop()
                print(f"Processing message {message.data} from {queue_name}")
                self.process_message(queue_name, message.data)
            time.sleep(1)

    def draw_state_machine(self):
        self.machine.get_graph().draw('state_diagram.png', prog='dot')