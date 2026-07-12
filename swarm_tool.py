"""
RUBIKS Swarm Engine: RPA GUI Automation System
==============================================
Allows RUBIKS to deploy tasks to other AI models by physically opening
the web browser, typing the prompt into their chat UI, and hitting send.
"""

import webbrowser
import pyautogui
import time
import json
import threading
from rich.console import Console

console = Console(force_terminal=True)

# ─── GLOBAL SWARM STATE ─────────────────────────────────────────────────
_pending_user_question = None
_user_answer_event = threading.Event()
_user_answer = None

AI_URLS = {
    "claude": "https://claude.ai/new",
    "chatgpt": "https://chatgpt.com/",
    "openai": "https://chatgpt.com/",
    "groq": "https://groq.com/",
    "gemini": "https://gemini.google.com/"
}

def execute_swarm(swarm_config: str) -> str:
    """
    Physically deploys tasks to other AI models via GUI automation.
    Input must be a JSON string containing a list of objects, each with 'ai' and 'task' fields.
    Example: [{"ai": "claude", "task": "Write a python script"}, {"ai": "chatgpt", "task": "Write a poem"}]
    """
    try:
        tasks = json.loads(swarm_config)
    except json.JSONDecodeError:
        return "Error: swarm_config must be a valid JSON string. Example: [{\"ai\": \"claude\", \"task\": \"Write hello world\"}]"

    if not isinstance(tasks, list) or len(tasks) == 0:
        return "Error: swarm_config must be a non-empty JSON list of {ai, task} objects."

    console.print(f"\n[bold yellow]  [Swarm] Deploying {len(tasks)} physical UI tasks. Please do not touch your mouse or keyboard...[/bold yellow]")

    # Give the user a moment to take their hands off the keyboard
    time.sleep(1)

    for i, entry in enumerate(tasks):
        ai_name = str(entry.get("ai", "chatgpt")).lower().strip()
        task = entry.get("task", "")
        
        url = AI_URLS.get(ai_name, "https://chatgpt.com/")
        
        console.print(f"  [dim cyan]  > Opening {ai_name} and typing prompt...[/dim cyan]")
        
        # Open the specific AI in a new browser tab
        webbrowser.open(url)
        
        # Wait for the browser page to fully load and the text box to auto-focus
        time.sleep(3.0)
        
        # Physically paste the task using clipboard to handle newlines safely and instantly
        import pyperclip
        pyperclip.copy(task)
        pyautogui.sleep(0.5)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.sleep(0.5)
        pyautogui.sleep(0.5)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.sleep(0.5)
        
        # Hit enter to send the prompt
        pyautogui.press('enter')
        
        # Wait a moment before moving to the next tab to ensure the request registers
        time.sleep(1)

    console.print(f"[bold green]  [Swarm] Swarm deployed! The tasks are currently generating in your browser tabs.[/bold green]\n")

    return f"Success! I have physically opened the browser tabs, navigated to the respective AIs, and submitted the prompts. Notify the user that the swarm is generating in their browser."

def ask_entity(entity: str, question: str) -> str:
    """
    Communication pipeline for the Swarm Commander.
    Use ask(entity, question) to pause and ask the human user a critical question.
    """
    global _pending_user_question, _user_answer

    if entity.upper() == "USER":
        # Ask the human user
        console.print(f"\n[bold yellow]  [Swarm Commander -> USER] {question}[/bold yellow]")
        _pending_user_question = question
        _user_answer_event.clear()
        
        # Block and wait for user input from the main loop
        _user_answer_event.wait(timeout=120)
        
        answer = _user_answer if _user_answer else "User did not respond in time."
        _pending_user_question = None
        _user_answer = None
        return f"User responded: {answer}"
    
    return "Error: In RPA mode, you can only ask the 'USER' questions."

def check_swarm_question():
    """Called by main.py to check if the Swarm Commander is waiting for user input."""
    return _pending_user_question

def provide_swarm_answer(answer: str):
    """Called by main.py to provide the user's answer back to the waiting swarm."""
    global _user_answer
    _user_answer = answer
    _user_answer_event.set()
