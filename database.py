import sqlite3
import json
import uuid
import os

# Database Handler
class Database:
    def __init__(self, db_name="messages.db"):
        db_path = os.path.join("dbs", db_name)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA journal_mode=WAL;")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                data TEXT,
                state TEXT
            )
        """)
        self.conn.commit()

    def save_message(self, data):
        message_id = str(uuid.uuid4())
        self.cursor.execute("INSERT INTO messages (id, data, state) VALUES (?, ?, ?)", (message_id, json.dumps(data), 'start'))
        self.conn.commit()
        return message_id

    def get_message(self, message_id):
        self.cursor.execute("SELECT data, state FROM messages WHERE id = ?", (message_id,))
        row = self.cursor.fetchone()
        return (json.loads(row[0]), row[1]) if row else (None, None)

    def update_message(self, message_id, data, state):
        self.cursor.execute("UPDATE messages SET data = ?, state = ? WHERE id = ?", (json.dumps(data), state, message_id))
        self.conn.commit()