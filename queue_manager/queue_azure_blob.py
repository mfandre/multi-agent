from azure.storage.queue import QueueServiceClient
import json
from config import AZURE_CONNECTION_STRING
from queue_manager.queue_manager import QueueManager

class AzureQueue(QueueManager):
    def __init__(self, topic:str):
        self.queue_service = QueueServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        self.queue_client = self.queue_service.get_queue_client(topic)

    def send_message(self, message: dict):
        self.queue_client.send_message(json.dumps(message))

    def receive_messages(self):
        return self.queue_client.receive_messages()

    def delete_message(self, message_id):
        self.queue_client.delete_message(message_id)