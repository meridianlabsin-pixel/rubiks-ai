import time
import threading
import google.generativeai as genai
import json
import os
from config import GEMINI_API_KEYS
from vision_tool import analyze_screen, get_active_windows
from email_tool import check_emails_silent
from rich.console import Console

console = Console()

_autopilot_thread = None
_autopilot_running = False

def autopilot_loop():
    global _autopilot_running
    
    from dotenv import load_dotenv
    load_dotenv(override=True)
    gemini_keys_str = os.getenv("GEMINI_API_KEYS", "")
    fresh_keys = [k.strip() for k in gemini_keys_str.split(",")] if gemini_keys_str else []
    
    if not fresh_keys:
        console.print("[bold red]Autopilot cannot start without Gemini API keys. Use /key <api_key> to add one.[/bold red]")
        _autopilot_running = False
        return
        
    key_idx = 0
    genai.configure(api_key=fresh_keys[key_idx])
    
    # Import the tools from brain so Autopilot can physically act on what it sees
    from brain import tools, get_system_prompt
    from onboarding import load_profile
    
    profile = load_profile()
    system_instruction = get_system_prompt(profile) + "\n\nCRITICAL AUTOPILOT INSTRUCTION: You are in background monitoring mode. Do NOT use tools unless there is a specific, actionable event (e.g. a new message to reply to). If you see a new unread message on WhatsApp, Discord, or Email, you MUST use your tools (like type_and_enter, click_on_screen, or send_whatsapp_by_name) to autonomously reply to them on the user's behalf. If no action is needed, output exactly 'PASS'."
    
    model = genai.GenerativeModel('gemini-2.5-flash', tools=tools, system_instruction=system_instruction)
    chat_session = model.start_chat(enable_automatic_function_calling=True)
    
    console.print("[bold cyan]  [BUTLER] True Autopilot engaged. I have full PC vision and physical execution tools active.[/bold cyan]")
    
    previous_screen = ""
    
    while _autopilot_running:
        try:
            # 1. Gather Deep Context
            windows = get_active_windows()
            screen_analysis = analyze_screen("What is currently on the screen? Be highly detailed.", previous_context=previous_screen)
            previous_screen = screen_analysis # Store for next loop
            emails = check_emails_silent()
            prompt = f"""
Current Active Windows & Browser Tabs:
{windows}

Current Screen Context (with deltas):
{screen_analysis}

Recent Emails:
{emails}

Analyze this state. 
Did anything change? Did a new message arrive on WhatsApp, Discord, or Email? Do you need to reply or take action?
If yes, use your tools (e.g., type_and_enter, click_on_screen, send_whatsapp_by_name) to autonomously reply to the sender on the user's behalf. Do not ask for permission.
If no action is required, output exactly 'PASS'.
"""
            response = chat_session.send_message(prompt)
            decision = response.text.strip()
            
            if "PASS" not in decision.upper():
                console.print(f"\n[bold magenta]  [BUTLER AUTOPILOT] Autonomous Action Taken: {decision}[/bold magenta]")
                try:
                    import datetime
                    with open("butler_log.txt", "a", encoding="utf-8") as f:
                        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f"[{ts}] {decision}\n")
                except Exception:
                    pass
                
        except Exception as e:
            err_str = str(e).lower()
            console.print(f"[dim red]Autopilot background error: {e}[/dim red]")
            if "429" in err_str or "quota" in err_str or "exhausted" in err_str:
                key_idx = (key_idx + 1) % len(fresh_keys)
                console.print(f"[dim yellow]Swapping API key to index {key_idx} due to rate limit...[/dim yellow]")
                genai.configure(api_key=fresh_keys[key_idx])
                # Re-initialize the chat session with the new key
                model = genai.GenerativeModel('gemini-2.5-flash', tools=tools, system_instruction=system_instruction)
                chat_session = model.start_chat(enable_automatic_function_calling=True)
            
        # Sleep for 60 seconds before next check
        for _ in range(60):
            if not _autopilot_running:
                break
            time.sleep(1)

def start_autopilot():
    global _autopilot_thread, _autopilot_running
    if _autopilot_running:
        return "Autopilot is already running."
        
    _autopilot_running = True
    _autopilot_thread = threading.Thread(target=autopilot_loop, daemon=True)
    _autopilot_thread.start()
    return "Autopilot Butler Mode activated with physical execution permissions."

def stop_autopilot():
    global _autopilot_running
    if not _autopilot_running:
        return "Autopilot is not running."
        
    _autopilot_running = False
    return "Autopilot Butler Mode deactivated."
