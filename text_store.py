import os
import json
import uuid

TEXT_STORAGE_DIR = "temp_text_storage"

# Garantir que o diretório existe
os.makedirs(TEXT_STORAGE_DIR, exist_ok=True)

def save_text(text:str, text_id: str = None):
    """Salva o texto em um arquivo local e retorna um ID único."""
    text_id = text_id if text_id is not None else str(uuid.uuid4())  # Gera um ID único
    file_path = os.path.join(TEXT_STORAGE_DIR, f"{text_id}.txt")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    return text_id

def load_text(text_id:str):
    """Carrega o texto a partir do ID."""
    file_path = os.path.join(TEXT_STORAGE_DIR, f"{text_id}.txt")
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return None