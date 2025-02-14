from abc import ABC, abstractmethod
import json

class QueueManager(ABC):
    @abstractmethod
    def send_message(self, message: dict):
        pass

    @abstractmethod
    def receive_messages(self):
        pass

    @abstractmethod
    def delete_message(self, message_id):
        pass