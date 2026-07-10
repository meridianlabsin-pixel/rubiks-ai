import os
import psutil
import pyautogui
import subprocess
import webbrowser
import urllib.parse
import sys

def get_system_stats() -> str:
    """Returns the current CPU and RAM usage."""
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    return f"CPU Usage: {cpu}%, RAM Usage: {ram}%"

def open_application(app_name: str) -> str:
    """Attempts to open a standard Windows application."""
    # A simple mapping of common apps
    app_map = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "chrome": "chrome.exe",
        "edge": "msedge.exe",
        "explorer": "explorer.exe",
        "spotify": "spotify.exe",
        "comet": "comet.exe"
    }
    
    # --- AUTO-ROUTING FAILSAFE ---
    # If the AI accidentally sends a filename to the application launcher,
    # detect the file extension and automatically reroute it to the file system engine.
    import os
    
    # --- PRONOUN RESOLUTION FAILSAFE ---
    # If the AI literally tries to open "it" or "that", it means the user just asked 
    # about a recent file and then said "open it". Automatically fetch the most recent file.
    if app_name.lower().strip() in ["it", "that", "this", "the file", "the image", "the photo", "the document"]:
        try:
            from file_tools import find_recent_files, open_file
            # Get the raw path of the most recent file
            recent_data = find_recent_files(count=1)
            # The last element in the recent file string is the absolute path
            path = recent_data.strip().split(" - ")[-1]
            if os.path.exists(path):
                return open_file(path)
        except Exception:
            pass

    _, ext = os.path.splitext(app_name)
    if ext.lower() in [".jpg", ".jpeg", ".png", ".pdf", ".txt", ".docx", ".mp4", ".mp3", ".xlsx", ".pptx", ".csv", ".json", ".zip"]:
        try:
            from file_tools import open_file
            return open_file(app_name)
        except Exception:
            pass
            
    
    if app_name.lower() in ["whatsapp", "whatsapp web"]:
        return open_website("https://web.whatsapp.com")
        
    executable = app_map.get(app_name.lower())
    if executable:
        try:
            os.startfile(executable)
            return f"Successfully opened {app_name}."
        except Exception as e:
            pass

    # Safeguard against the AI passing entire sentences
    if len(app_name.split()) > 3:
        return f"Error: '{app_name}' is too long to be an app. If you are trying to type a message or search, use the 'type_text' or 'search_web' tools instead."

    # Fallback to pressing the Windows key and typing the app name
    try:
        pyautogui.press('win')
        pyautogui.sleep(1)
        pyautogui.write(app_name)
        pyautogui.sleep(1)
        pyautogui.press('enter')
        return f"Attempted to open {app_name} via Start menu search."
    except Exception as e:
        return f"Failed to open {app_name}. Error: {str(e)}"

def open_website(query: str) -> str:
    """Opens the user's default browser (Comet) and navigates to the URL or searches the query."""
    try:
        # Check if the query is a URL
        if query.startswith("http://") or query.startswith("https://") or ("." in query and " " not in query):
            if not query.startswith("http"):
                url = f"https://{query}"
            else:
                url = query
        else:
            # Otherwise, perform a web search and grab the VERY FIRST link
            from googlesearch import search
            results = list(search(query, num_results=1))
            if results:
                url = results[0]
            else:
                return f"Could not find any Google results for: {query}"
            
        # Use the system default browser
        webbrowser.open(url)
            
        return f"Successfully opened the first Google result for '{query}' in the default browser."
    except Exception as e:
        return f"Failed to open browser: {str(e)}"

def run_terminal_command(command: str) -> str:
    """Executes a command in PowerShell and returns the output."""
    try:
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            return result.stdout.strip() if result.stdout else "Command executed successfully with no output."
        else:
            return f"Command failed: {result.stderr.strip()}"
    except Exception as e:
        return f"Error executing command: {str(e)}"

def type_text(text: str) -> str:
    """Types the provided text using the keyboard. Supports {tab}, {enter}, {backspace}, etc."""
    try:
        import re
        parts = re.split(r'(\{[a-zA-Z0-9_]+\})', text)
        for part in parts:
            if not part:
                continue
            if part.startswith('{') and part.endswith('}'):
                key = part[1:-1].lower()
                try:
                    pyautogui.press(key)
                except Exception:
                    pass
            else:
                try:
                    import pyperclip
                    pyperclip.copy(part)
                    pyautogui.sleep(0.05)
                    pyautogui.hotkey('ctrl', 'v')
                    pyautogui.sleep(0.05)
                except ImportError:
                    # Fallback if pyperclip is not installed
                    pyautogui.write(part, interval=0.01)
        return "Text typed successfully."
    except Exception as e:
        return f"Failed to type text: {str(e)}"

def type_and_enter(text: str) -> str:
    """Types the provided text using the keyboard and then presses the Enter key. Use this to send messages in active chats."""
    try:
        import pygetwindow as gw
        
        # Try to find WhatsApp or Comet windows
        target_window = None
        for win in gw.getAllWindows():
            title = win.title.lower()
            if 'whatsapp' in title or 'comet' in title or 'chrome' in title:
                target_window = win
                break
                
        if target_window:
            try:
                target_window.restore()
                target_window.activate()
                pyautogui.sleep(0.5)
                # Click the center of the window to ensure the input field is ready
                pyautogui.click(target_window.center.x, target_window.center.y + 200)
                pyautogui.sleep(0.2)
            except Exception:
                pass
        
        type_text(text)
        pyautogui.press('enter')
        return "Text typed and entered successfully."
    except Exception as e:
        return f"Failed to type and enter text: {str(e)}"

def execute_python_script(code: str) -> str:
    """Writes the provided Python code to a sandbox file and executes it, returning the output. Useful for math, file sorting, or autonomous problem solving."""
    sandbox_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rubiks_sandbox.py")
    try:
        with open(sandbox_path, "w", encoding="utf-8") as f:
            f.write(code)
            
        result = subprocess.run(
            [sys.executable, sandbox_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout
        if result.stderr:
            output += f"\nErrors:\n{result.stderr}"
        return output.strip() if output.strip() else "Script executed successfully with no output."
    except Exception as e:
        return f"Script execution failed: {str(e)}"
