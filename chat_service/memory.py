conversation_memory = {}


def get_memory(session_id):
    return conversation_memory.get(session_id, [])


def save_memory(session_id, messages):
    conversation_memory[session_id] = messages[-10:]  # keep last 10
