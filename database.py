import sqlite3
import json
import uuid
import os

# Database Handler
class Database:
    def __init__(self, db_name="messages.db"):
        self.db_path = os.path.join("dbs", db_name)
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                data TEXT,
                state TEXT
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()

    def save_message(self, data):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        message_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO messages (id, data, state) VALUES (?, ?, ?)", (message_id, json.dumps(data), 'start'))
        conn.commit()
        cursor.close()
        conn.close()
        return message_id

    def get_message(self, message_id):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT data, state FROM messages WHERE id = ?", (message_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return (json.loads(row[0]), row[1]) if row else (None, None)
        

    def update_message(self, message_id, data, state = None):
        if state is None:
            curr_msg, curr_state = self.get_message(message_id)
            state = curr_state

        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("UPDATE messages SET data = ?, state = ? WHERE id = ?", (json.dumps(data), state, message_id))
        conn.commit()
        cursor.close()
        conn.close()
