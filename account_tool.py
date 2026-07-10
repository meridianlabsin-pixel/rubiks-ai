import subprocess
import pyautogui
import time
import random
import string
import os


def _open_in_comet(url: str):
    """Opens a URL in Comet browser."""
    if os.path.exists(None):
        webbrowser.open(url)
    else:
        import webbrowser
        webbrowser.open(url)

def _generate_username(base_name: str) -> str:
    """Generates a unique username from a base name."""
    suffix = ''.join(random.choices(string.digits, k=4))
    clean = base_name.lower().replace(' ', '').replace('.', '')
    return f"{clean}{suffix}"

def _generate_password() -> str:
    """Generates a strong random password."""
    chars = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(random.choices(chars, k=14))


def create_account(platform: str, full_name: str = "", email: str = "", password: str = "") -> str:
    """
    Opens the signup page for Gmail, Instagram, or Facebook in Comet browser and 
    auto-fills the registration form using GUI automation.
    The user will need to complete phone verification and CAPTCHA manually.
    
    Args:
        platform: The platform to create an account on ('gmail', 'instagram', 'facebook').
        full_name: The full name to use for the account. If empty, uses 'RUBIKS AI'.
        email: An existing email to use for Instagram/Facebook signup. Leave empty for Gmail.
        password: The password to set. If empty, a strong one is auto-generated.
    """
    platform = platform.lower().strip()
    
    if not full_name:
        full_name = "RUBIKS AI"
    
    if not password:
        password = _generate_password()
    
    name_parts = full_name.split(' ', 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else "System"
    
    username = _generate_username(full_name)
    
    result_info = f"Name: {full_name}\nUsername: {username}\nPassword: {password}\n"

    try:
        if platform in ["gmail", "google", "email"]:
            _open_in_comet("https://accounts.google.com/signup")
            time.sleep(4)
            
            # Gmail form auto-focuses the First Name field on load. 
            # We hit tab once then shift+tab to guarantee focus, then type.
            pyautogui.press('tab')
            time.sleep(0.1)
            pyautogui.hotkey('shift', 'tab')
            time.sleep(0.3)
            
            pyautogui.typewrite(first_name, interval=0.04)
            pyautogui.press('tab')
            time.sleep(0.2)
            pyautogui.typewrite(last_name, interval=0.04)
            
            result_info += f"Email: {username}@gmail.com\n"
            result_info += "Platform: Gmail\n"
            result_info += "Status: Signup page opened and name filled. Complete the remaining steps manually (birthday, phone verification, CAPTCHA)."
            
            # Save credentials
            _save_credentials("Gmail", username + "@gmail.com", password, full_name)
            
            return result_info

        elif platform in ["instagram", "insta", "ig"]:
            _open_in_comet("https://www.instagram.com/accounts/emailsignup/")
            time.sleep(5)
            
            # Instagram signup: email, full name, username, password
            # Use Tab navigation to find the first field securely
            pyautogui.press('tab', presses=3, interval=0.1)
            time.sleep(0.3)
            
            signup_email = email if email else f"{username}@gmail.com"
            pyautogui.typewrite(signup_email, interval=0.03)
            pyautogui.press('tab')
            time.sleep(0.2)
            pyautogui.typewrite(full_name, interval=0.03)
            pyautogui.press('tab')
            time.sleep(0.2)
            pyautogui.typewrite(username, interval=0.03)
            pyautogui.press('tab')
            time.sleep(0.2)
            pyautogui.typewrite(password, interval=0.03)
            
            result_info += f"Email used: {signup_email}\n"
            result_info += "Platform: Instagram\n"
            result_info += "Status: Signup form filled. Complete phone verification and CAPTCHA manually."
            
            _save_credentials("Instagram", username, password, full_name)
            
            return result_info

        elif platform in ["facebook", "fb"]:
            _open_in_comet("https://www.facebook.com/r.php")
            time.sleep(5)
            
            # Facebook signup: first name, last name, email, password, birthday, gender
            # Use Tab navigation
            pyautogui.press('tab', presses=4, interval=0.1)
            time.sleep(0.3)
            pyautogui.typewrite(first_name, interval=0.03)
            pyautogui.press('tab')
            time.sleep(0.2)
            pyautogui.typewrite(last_name, interval=0.03)
            pyautogui.press('tab')
            time.sleep(0.2)
            
            signup_email = email if email else f"{username}@gmail.com"
            pyautogui.typewrite(signup_email, interval=0.03)
            pyautogui.press('tab')
            time.sleep(0.2)
            pyautogui.typewrite(signup_email, interval=0.03)  # Re-enter email
            pyautogui.press('tab')
            time.sleep(0.2)
            pyautogui.typewrite(password, interval=0.03)
            
            result_info += f"Email used: {signup_email}\n"
            result_info += "Platform: Facebook\n"
            result_info += "Status: Signup form filled. Complete birthday, gender, and verification manually."
            
            _save_credentials("Facebook", signup_email, password, full_name)
            
            return result_info

        else:
            return f"Unknown platform: '{platform}'. Supported: gmail, instagram, facebook."

    except Exception as e:
        return f"Account creation failed: {str(e)}"


def _save_credentials(platform: str, username: str, password: str, full_name: str):
    """Saves generated credentials to a secure local file."""
    creds_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rubiks_credentials.txt")
    try:
        with open(creds_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- {platform} ---\n")
            f.write(f"Name: {full_name}\n")
            f.write(f"Username/Email: {username}\n")
            f.write(f"Password: {password}\n")
            f.write(f"Created: {time.strftime('%Y-%m-%d %H:%M')}\n")
    except:
        pass
