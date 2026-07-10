import pyautogui
import time
import pyperclip

def send_whatsapp_by_name(contact_name: str, message: str) -> str:
    """Sends a WhatsApp message to a contact by searching for their NAME inside WhatsApp.
    This works whether WhatsApp Desktop app or WhatsApp Web is open.
    Does NOT require a phone number — it searches by name like a human would.
    
    Args:
        contact_name: The name of the contact to message (e.g. "John", "Mom", "Boss").
        message: The message text to send.
    """
    try:
        import pygetwindow as gw
        
        # Step 1: Find and focus the WhatsApp window
        whatsapp_window = None
        for win in gw.getAllWindows():
            title = (win.title or "").lower()
            if "whatsapp" in title:
                whatsapp_window = win
                break
        
        if not whatsapp_window:
            # WhatsApp is not open — try to open it
            import subprocess
            try:
                # Try WhatsApp Desktop app first
                subprocess.Popen(["start", "whatsapp:"], shell=True)
                time.sleep(4)
                # Re-check
                for win in gw.getAllWindows():
                    title = (win.title or "").lower()
                    if "whatsapp" in title:
                        whatsapp_window = win
                        break
            except Exception:
                pass
                
            if not whatsapp_window:
                return "WhatsApp is not open and could not be launched. Please open WhatsApp first."
        
        # Step 2: Bring WhatsApp to the foreground
        try:
            whatsapp_window.restore()
            whatsapp_window.activate()
            time.sleep(0.5)
        except Exception:
            pass
        
        # Step 3: Open the search bar (Ctrl+F or click the search icon area)
        # WhatsApp Desktop and Web both support Ctrl+F or clicking the search
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.5)
        
        # Step 4: Clear any existing search text and type the contact name
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyperclip.copy(contact_name)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1.5)  # Wait for search results to populate
        
        # Step 5: Press Enter or Down+Enter to select the first search result
        pyautogui.press('enter')
        time.sleep(1.0)
        
        # Step 6: Now the chat is open. Click the message input area.
        # The message box is typically at the bottom of the window.
        # We press Escape first to close the search panel, then Tab to the message box.
        pyautogui.press('escape')
        time.sleep(0.3)
        
        # Click the message input box (bottom center of the WhatsApp window)
        if whatsapp_window:
            box_x = whatsapp_window.left + int(whatsapp_window.width * 0.65)
            box_y = whatsapp_window.top + whatsapp_window.height - 40
            pyautogui.click(box_x, box_y)
            time.sleep(0.3)
        
        # Step 7: Type the message using clipboard (handles emojis and special chars)
        pyperclip.copy(message)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.2)
        
        # Step 8: Send it
        pyautogui.press('enter')
        
        return f"Message sent to '{contact_name}' on WhatsApp: \"{message}\""
        
    except Exception as e:
        return f"Failed to send WhatsApp message to {contact_name}: {str(e)}"


def send_whatsapp_message(phone_number: str, message: str) -> str:
    """Sends a WhatsApp message to a phone number via WhatsApp Web URL.
    The phone_number MUST include the country code without any + or spaces (e.g. 919876543210).
    Only use this if you have the EXACT phone number. If you only have a name, use send_whatsapp_by_name instead.
    """
    try:
        import webbrowser
        import urllib.parse
        import threading
        
        phone = "".join(filter(str.isdigit, str(phone_number)))
        if not phone:
            return "Invalid phone number provided."
            
        encoded_message = urllib.parse.quote(message)
        url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
        
        webbrowser.open(url)
        
        def _press_enter_later():
            pyautogui.sleep(15)
            try:
                import pygetwindow as gw
                active_window = gw.getActiveWindow()
                if active_window and "WhatsApp" in active_window.title:
                    pyautogui.press('enter')
            except ImportError:
                pyautogui.press('enter')
        
        threading.Thread(target=_press_enter_later, daemon=True).start()
        
        return f"WhatsApp message initiated to {phone}. It will send automatically in 15 seconds once the page loads."
    except Exception as e:
        return f"Failed to send WhatsApp message: {str(e)}"
