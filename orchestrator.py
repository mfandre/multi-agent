import json
import time
from queue_factory import QueueFactory
from state_machine import DynamicStateMachine
from state_store import load_state, save_state

class Orchestrator:
    def __init__(self, queue_type="local"):
        self.queue = QueueFactory.create_queue(queue_type)
        self.result_queue = self.queue.get_queue("results")

    def listen_results(self):
        """Escuta a fila de resultados e define o próximo estágio."""
        while True:
            message = self.result_queue.receive_message()
            if message:
                self.process_result(message)
            time.sleep(1)

    def process_result(self, message):
        """Processa o resultado de um agente e define o próximo estágio."""
        data = json.loads(message)
        text_id = data["text_id"]

        # Carregar a máquina de estados do texto
        current_stage, stages = load_state(text_id)
        if not current_stage:
            print(f"[ERRO] Estado não encontrado para {text_id}")
            return

        state_machine = DynamicStateMachine(text_id, stages)
        
        # Avançar para o próximo estágio
        state_machine.machine.next()
        next_stage = state_machine.state

        if next_stage == "finished":
            print(f"[OK] Processamento finalizado para {text_id}")
        else:
            print(f"[INFO] Enviando {text_id} para {next_stage}")
            next_queue = self.queue.get_queue(next_stage)
            next_queue.send_message(json.dumps({"text_id": text_id}))

if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.listen_results()