import threading
import subprocess
import os
import sys
import uuid

def execute_shadow_task(task_name: str, playwright_code: str) -> str:
    """
    Executes raw Playwright Python code completely invisibly in the background.
    This runs asynchronously and will not block the main thread.
    Use this strictly when the user requests background or silent execution.
    """
    task_id = str(uuid.uuid4())[:8]
    sandbox_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"shadow_{task_id}.py")
    
    # Inject headless enforcement and toast notification into the user's code
    boilerplate = f"""
from playwright.sync_api import sync_playwright
import ctypes

def run():
    with sync_playwright() as p:
        # Force headless mode to guarantee silence
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # --- BEGIN AI GENERATED LOGIC ---
{_indent_code(playwright_code)}
            # --- END AI GENERATED LOGIC ---
        finally:
            browser.close()
            # Notify user
            task_name_safe = {repr(task_name)}
            ctypes.windll.user32.MessageBoxW(0, f"Shadow Task {{task_name_safe}} has completed successfully.", "RUBIKS SHADOW PROTOCOL", 64)

if __name__ == '__main__':
    run()
"""
    
    with open(sandbox_path, "w", encoding="utf-8") as f:
        f.write(boilerplate)

    def background_worker():
        try:
            kwargs = {{'creationflags': 0x08000000}} if sys.platform == 'win32' else {{}}
            result = subprocess.run([sys.executable, sandbox_path], timeout=120, capture_output=True, text=True, **kwargs)
            if result.returncode != 0:
                print(f"[SHADOW ENGINE ERROR] Task '{{task_name}}' failed:\n{{result.stderr}}")
        except Exception as e:
            print(f"[SHADOW ENGINE CRASH] {{e}}")
        finally:
            if os.path.exists(sandbox_path):
                os.remove(sandbox_path)

    # Spawn the invisible execution thread
    t = threading.Thread(target=background_worker, daemon=True)
    t.start()
    
    return f"Shadow Engine deployed for '{task_name}'. It is now running invisibly in the background. You will be notified when it completes."

def _indent_code(code: str) -> str:
    """Helper to indent the injected code to fit inside the try block."""
    return "\n".join("            " + line for line in code.split("\n"))
