import threading
import time
from state_machine import DynamicStateMachine
from config import WORKFLOW_CONFIG
from agents.filter_agent import filter_agent
from agents.markdown_agent import markdown_agent
from agents.sentiment_agent import sentiment_agent
from agents.spell_check_agent import spellcheck_agent

if __name__ == "__main__":
    sm = DynamicStateMachine(WORKFLOW_CONFIG)

    sm.process("input")

    threading.Thread(target=filter_agent, daemon=True).start()
    threading.Thread(target=sentiment_agent, daemon=True).start()
    threading.Thread(target=spellcheck_agent, daemon=True).start()
    threading.Thread(target=markdown_agent, daemon=True).start()

    time.sleep(5)