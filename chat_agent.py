"""
RUBIKS Autonomous Chat Replier Agent.

A mini-RUBIKS agent that runs in a background thread, continuously watching
the screen for new chat messages and auto-replying to them using Gemini AI.
"""

import warnings
warnings.filterwarnings('ignore')

import threading
import pyautogui
import time
import os
import tempfile
import google.generativeai as genai

# Module-level state
_chat_thread = None
_stop_event = threading.Event()


def _chat_loop(platform: str) -> None:
    """Internal loop that screenshots the screen, sends to Gemini, and auto-replies."""
    try:
        from pc_controller import type_and_enter
        from dotenv import load_dotenv
        load_dotenv(override=True)
        gemini_keys_str = os.environ.get("GEMINI_API_KEYS", "")
        fresh_keys = [k.strip() for k in gemini_keys_str.split(",")] if gemini_keys_str else []
        
        if not fresh_keys:
            print("[MINI-RUBIKS] No API keys found. Please set them using /key first.", flush=True)
            return
            
        genai.configure(api_key=fresh_keys[0])
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        last_reply = ""
        
        while not _stop_event.is_set():
            try:
                # Take a screenshot
                screenshot = pyautogui.screenshot()

                # Save to a temp file
                tmp_path = os.path.join(tempfile.gettempdir(), 'rubiks_chat_screen.png')
                screenshot.save(tmp_path)
                
                # Contextual prompt
                prompt = (
                    f"Look at this chat screen. You are the user on the right side. "
                    f"The last message you sent was: '{last_reply}'.\n"
                    f"Has the other person replied with something new that requires an answer? "
                    f"If yes, generate a natural, friendly, Gen-Z style reply. "
                    f"If no (they haven't said anything new, or no reply is needed), you MUST respond with the exact word NOTHING. "
                    f"Only output the reply text, nothing else."
                )

                # Use a random API key to avoid 429 ResourceExhausted
                import random
                from dotenv import load_dotenv
                load_dotenv(override=True)
                gemini_keys_str = os.environ.get("GEMINI_API_KEYS", "")
                fresh_keys = [k.strip() for k in gemini_keys_str.split(",")] if gemini_keys_str else []
                if fresh_keys:
                    active_key = random.choice(fresh_keys)
                    genai.configure(api_key=active_key)
                
                model = genai.GenerativeModel('gemini-2.5-flash')

                # Upload image and ask Gemini for a reply
                print(f"\n[MINI-RUBIKS] Scanning screen... (Last sent: '{last_reply}')", flush=True)
                uploaded_file = genai.upload_file(tmp_path)
                response = model.generate_content([prompt, uploaded_file])
                reply_text = response.text.strip()
                
                print(f"[MINI-RUBIKS] AI Decision: {reply_text}", flush=True)

                # If Gemini returned a real reply, type and send it
                if reply_text and reply_text.upper() != 'NOTHING' and not reply_text.startswith("NOTHING"):
                    print(f"[MINI-RUBIKS] Executing reply: {reply_text}", flush=True)
                    type_and_enter(reply_text)
                    last_reply = reply_text
                else:
                    print("[MINI-RUBIKS] No new messages detected. Waiting...", flush=True)

            except Exception as e:
                print(f"[MINI-RUBIKS] Error in loop: {str(e)}", flush=True)
                pass

            # Wait 5 seconds before next check to give time for UI updates
            _stop_event.wait(timeout=5)

    except Exception as e:
        print(f"[MINI-RUBIKS] Fatal Error: {str(e)}", flush=True)


def start_chat_agent(platform: str = "whatsapp") -> str:
    """Starts the autonomous chat agent in a background thread.

    The agent takes a screenshot every 5 seconds, sends it to Gemini for
    analysis, and if a reply is needed, types and sends it automatically.

    Args:
        platform: The chat platform to monitor (default: 'whatsapp').

    Returns:
        A status message indicating the agent has started or is already running.
    """
    global _chat_thread
    try:
        if _chat_thread is not None and _chat_thread.is_alive():
            return f"Chat agent is already running on '{platform}'."

        _stop_event.clear()
        _chat_thread = threading.Thread(target=_chat_loop, args=(platform,), daemon=True)
        _chat_thread.start()
        return f"Chat agent started for '{platform}'. Monitoring screen every 5 seconds."
    except Exception as e:
        return f"Failed to start chat agent: {str(e)}"


def stop_chat_agent() -> str:
    """Stops the autonomous chat agent by signaling the background thread to exit.

    Returns:
        A status message indicating the agent has been stopped or was not running.
    """
    global _chat_thread
    try:
        if _chat_thread is None or not _chat_thread.is_alive():
            return "Chat agent is not running."

        _stop_event.set()
        _chat_thread.join(timeout=10)
        _chat_thread = None
        return "Chat agent stopped."
    except Exception as e:
        return f"Error stopping chat agent: {str(e)}"
