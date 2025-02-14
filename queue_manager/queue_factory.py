from queue_manager.queue_azure_blob import AzureQueue
from queue_manager.queue_manager import QueueManager
from queue_manager.queue_sqlite import SQLiteQueue

class QueueFactory:
    @staticmethod
    def get_queue(topic:str, queue_type="sqlite") -> QueueManager:
        """Retorna a implementação de fila com base no tipo escolhido."""
        queues = {
            "azure": AzureQueue,
            "sqlite": SQLiteQueue
        }

        if queue_type not in queues:
            raise ValueError(f"Tipo de fila '{queue_type}' não suportado.")
        
        return queues[queue_type](topic)