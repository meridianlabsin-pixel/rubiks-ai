import time

def generate_greeting() -> str:
    """Generates a brief, direct JARVIS greeting with the current local time."""
    t = time.localtime()
    hour = t.tm_hour
    
    if hour < 12:
        greeting = "Good morning, Boss."
    elif hour < 17:
        greeting = "Good afternoon, Boss."
    else:
        greeting = "Good evening, Boss."
        
    time_str = time.strftime("%I:%M %p", t)
    return f"{greeting} It is currently {time_str}. Systems are online."
