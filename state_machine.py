from transitions.extensions import GraphMachine
from queue_manager.queue_factory import QueueFactory

class DynamicStateMachine:
    def __init__(self, workflow_config):
        self.workflow = workflow_config
        self.state = "start"
        self.machine:GraphMachine = None

        states = list(workflow_config.keys())
        transitions = []

        for state, next_stage in workflow_config.items():
            if isinstance(next_stage, dict):
                for trigger_name, target_state in next_stage.items():
                    transitions.append({
                        "trigger": trigger_name,
                        "source": state,
                        "dest": target_state
                    })
            else:
                transitions.append({
                    "trigger": "next",
                    "source": state,
                    "dest": next_stage
                })

        self.machine = GraphMachine(model=self, states=states, transitions=transitions, initial="start")

    def get_next_state(self, force_current_state = None):
        """Get next state base on current state. If do you want to get next state based on false current state, pass the your false state in force_current_state parameter."""
        current_state = force_current_state if force_current_state is not None else self.state
        next_stage = self.workflow[current_state]
        if isinstance(next_stage, dict):
            next_multiple = ""
            for trigger_name, target_state in next_stage.items():
                next_multiple += target_state +"|"
            return next_multiple[:-1]
        else:
            return next_stage
    # def process(self, text_id, result=None):
    #     """Decide a transição com base no resultado e encaminha para o próximo tópico"""
    #     if self.state in self.workflow and isinstance(self.workflow[self.state], dict):
    #         trigger = result
    #     else:
    #         trigger = "next"

    #     if hasattr(self, trigger):
    #         getattr(self, trigger)()

    #         next_stage = self.state
    #         next_queue = f"{next_stage}"  # Define o próximo tópico
    #         queue_client = QueueFactory.get_queue(next_queue)
    #         queue_client.send_message({"text_id": text_id})  # Publica na fila do próximo agente

if __name__ == "__main__":
    from config import WORKFLOW_CONFIG
    state_machine = DynamicStateMachine(WORKFLOW_CONFIG)
    
    # state_machine.machine.get_graph().draw('state_diagram.png', prog='dot')
    print(state_machine.get_next_state())
    print(state_machine.get_next_state("sentiment_analysis"))
    print(state_machine.get_next_state("spell_check"))
    print(state_machine.get_next_state("markdown_converter"))
    
    state_machine.next()
    state_machine.next()
    state_machine.next()
    state_machine.next()
    print(state_machine.state)

    # print(state_machine.state)
    # state_machine.process("input")
    # print(state_machine.state)
    # state_machine.process("input")
    # print(state_machine.state)
    # state_machine.process("neutral")
    # print(state_machine.state)
    # state_machine.process("input")
    # print(state_machine.state)
    # state_machine.process("input")