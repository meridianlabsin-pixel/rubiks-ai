import json
import os

MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory.json")

def _load_memory() -> dict:
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def _save_memory(data: dict):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def remember_fact(topic: str, fact: str) -> str:
    """Saves a piece of information permanently into RUBIKS's long-term memory.
    Use this when the user tells you something important about themselves, their preferences, or facts you should know for the future.
    """
    memories = _load_memory()
    if topic not in memories:
        memories[topic] = []
    
    if fact not in memories[topic]:
        memories[topic].append(fact)
        _save_memory(memories)
        
    return f"Successfully remembered that {fact} under the topic '{topic}'."

def recall_memories(topic: str = None) -> str:
    """Recalls stored information from long-term memory. 
    If you don't know the topic, call this with topic=None to see a list of all known topics.
    """
    memories = _load_memory()
    if not memories:
        return "I don't have any memories stored yet."
        
    if topic:
        topic_lower = topic.lower()
        # fuzzy match
        for key in memories:
            if topic_lower in key.lower() or key.lower() in topic_lower:
                facts = "\n- ".join(memories[key])
                return f"Here is what I remember about '{key}':\n- {facts}"
        return f"I couldn't find any specific memories about '{topic}'."
    else:
        topics = ", ".join(memories.keys())
        return f"I have memories stored about the following topics: {topics}"
