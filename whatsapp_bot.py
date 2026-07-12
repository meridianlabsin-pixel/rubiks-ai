"""
whatsapp_bot.py - Automated WhatsApp Web messaging using Playwright.
Uses a persistent browser profile so you only scan QR once.
"""
import os
import time
import threading
from playwright.sync_api import sync_playwright

_PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.whatsapp_profile')
_browser = None
_page = None
_lock = threading.Lock()
_ready = False

def _ensure_profile_dir():
    os.makedirs(_PROFILE_DIR, exist_ok=True)

def init_whatsapp(headless=False):
    """Launch WhatsApp Web with persistent profile. First time requires QR scan."""
    global _browser, _page, _ready
    _ensure_profile_dir()
    
    try:
        pw = sync_playwright().start()
        _browser = pw.chromium.launch_persistent_context(
            _PROFILE_DIR,
            headless=headless,
            args=['--disable-blink-features=AutomationControlled'],
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        _page = _browser.pages[0] if _browser.pages else _browser.new_page()
        _page.goto('https://web.whatsapp.com/', wait_until='domcontentloaded', timeout=60000)
        
        print("[WHATSAPP] WhatsApp Web opened. Waiting for login...")
        
        # Wait for the main chat interface to appear (means logged in)
        # The search box is a reliable indicator
        try:
            _page.wait_for_selector('div[contenteditable="true"][data-tab="3"]', timeout=120000)
            _ready = True
            print("[WHATSAPP] WhatsApp Web is READY!")
            return True
        except Exception:
            print("[WHATSAPP] Timeout waiting for WhatsApp login. Please scan QR code manually.")
            # Keep browser open so user can scan
            try:
                _page.wait_for_selector('div[contenteditable="true"][data-tab="3"]', timeout=300000)
                _ready = True
                print("[WHATSAPP] WhatsApp Web is READY after manual QR scan!")
                return True
            except:
                print("[WHATSAPP] Failed to login to WhatsApp Web.")
                return False
    except Exception as e:
        print(f"[WHATSAPP] Failed to init: {e}")
        return False

def send_message(contact_name_or_number: str, message: str) -> bool:
    """Search for a contact by name or number and send a message."""
    global _page, _ready
    
    if not _ready or not _page:
        print(f"[WHATSAPP] Not ready. Cannot send to {contact_name_or_number}")
        return False
    
    with _lock:
        try:
            print(f"[WHATSAPP] Sending message to: {contact_name_or_number}")
            
            # Click on the search box
            search_box = _page.wait_for_selector('div[contenteditable="true"][data-tab="3"]', timeout=10000)
            if not search_box:
                print("[WHATSAPP] Could not find search box")
                return False
            
            search_box.click()
            time.sleep(0.3)
            
            # Clear any existing text and type the contact name
            _page.keyboard.press('Control+a')
            _page.keyboard.press('Backspace')
            time.sleep(0.2)
            
            # Type the contact name/number
            search_box.fill(contact_name_or_number)
            time.sleep(2)  # Wait for search results
            
            # Click the first search result
            # WhatsApp search results appear in a list
            try:
                # Try to find the contact in search results
                result = _page.wait_for_selector(f'span[title*="{contact_name_or_number}"]', timeout=5000)
                if result:
                    result.click()
                else:
                    # Fallback: press Enter to select first result
                    _page.keyboard.press('Enter')
            except:
                # Fallback: just press down arrow then enter 
                _page.keyboard.press('ArrowDown')
                time.sleep(0.3)
                _page.keyboard.press('Enter')
            
            time.sleep(1)
            
            # Find the message input box
            msg_box = _page.wait_for_selector('div[contenteditable="true"][data-tab="10"]', timeout=10000)
            if not msg_box:
                print("[WHATSAPP] Could not find message input box")
                return False
            
            msg_box.click()
            time.sleep(0.2)
            
            # Type the message line by line (Shift+Enter for newlines)
            lines = message.split('\n')
            for i, line in enumerate(lines):
                if line.strip():
                    msg_box.type(line, delay=5)
                if i < len(lines) - 1:
                    _page.keyboard.down('Shift')
                    _page.keyboard.press('Enter')
                    _page.keyboard.up('Shift')
            
            time.sleep(0.3)
            
            # Press Enter to send
            _page.keyboard.press('Enter')
            time.sleep(1)
            
            print(f"[WHATSAPP] Message sent to {contact_name_or_number}!")
            return True
            
        except Exception as e:
            print(f"[WHATSAPP] Error sending to {contact_name_or_number}: {e}")
            return False

def close_whatsapp():
    """Close the browser."""
    global _browser, _page, _ready
    _ready = False
    try:
        if _browser:
            _browser.close()
    except:
        pass

if __name__ == '__main__':
    print("Testing WhatsApp Bot...")
    init_whatsapp(headless=False)
    print("WhatsApp ready. Type a contact name to test:")
    contact = input("Contact: ")
    msg = input("Message: ")
    send_message(contact, msg)
    input("Press Enter to close...")
    close_whatsapp()
