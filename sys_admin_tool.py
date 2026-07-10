import psutil
import pyperclip
import platform
import os
import subprocess

def get_running_processes(limit: int = 15) -> str:
    """
    Returns a list of the top processes currently running on the system, 
    sorted by memory usage. Useful for finding what is slowing the PC down.
    """
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                mem = proc.info['memory_info'].rss / (1024 * 1024) # Convert to MB
                processes.append({'name': proc.info['name'], 'pid': proc.info['pid'], 'mem': mem})
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
                
        # Sort by memory usage descending
        processes = sorted(processes, key=lambda p: p['mem'], reverse=True)
        
        result = "Top Running Processes (by Memory):\n"
        for p in processes[:limit]:
            result += f"PID {p['pid']}: {p['name']} ({p['mem']:.1f} MB)\n"
            
        return result.strip()
    except Exception as e:
        return f"Failed to get processes: {str(e)}"

def kill_process(process_name: str) -> str:
    """
    Forcefully terminates a running process by its name (e.g. 'chrome.exe' or 'spotify').
    Use with caution.
    """
    try:
        process_name = process_name.lower()
        if not process_name.endswith('.exe'):
            process_name += '.exe'
            
        killed = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == process_name:
                    proc.kill()
                    killed += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
        if killed > 0:
            return f"Successfully terminated {killed} instance(s) of {process_name}."
        else:
            return f"Could not find any running process named {process_name}."
    except Exception as e:
        return f"Failed to kill process: {str(e)}"

def read_clipboard() -> str:
    """
    Reads the current text contents of the user's clipboard (what they last copied).
    """
    try:
        content = pyperclip.paste()
        if content:
            return f"Clipboard contents:\n{content}"
        return "The clipboard is currently empty or does not contain text."
    except Exception as e:
        return f"Failed to read clipboard: {str(e)}"

def write_clipboard(text: str) -> str:
    """
    Writes text directly to the user's clipboard so they can paste it later.
    """
    try:
        pyperclip.copy(text)
        return "Successfully copied text to clipboard."
    except Exception as e:
        return f"Failed to write to clipboard: {str(e)}"

def set_system_volume(level: int) -> str:
    """
    Sets the Windows system volume (0 to 100).
    """
    try:
        if not (0 <= int(level) <= 100):
            return "Volume level must be between 0 and 100."
            
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        except ImportError:
            return "Missing required audio libraries. Please run: pip install pycaw comtypes"
            
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        # Scalar volume takes a float from 0.0 to 1.0
        scalar = float(level) / 100.0
        volume.SetMasterVolumeLevelScalar(scalar, None)
        
        return f"System volume set to {level}%."
    except Exception as e:
        return f"Failed to set volume: {str(e)}"

def get_system_info() -> str:
    """
    Returns deep hardware information about the system.
    """
    try:
        uname = platform.uname()
        mem = psutil.virtual_memory()
        
        info = f"System: {uname.system} {uname.release} (Build {uname.version})\n"
        info += f"Processor: {uname.processor}\n"
        info += f"Total RAM: {mem.total / (1024**3):.1f} GB ({mem.percent}% used)\n"
        
        # Get battery if available
        if hasattr(psutil, "sensors_battery"):
            batt = psutil.sensors_battery()
            if batt:
                info += f"Battery: {batt.percent}% (Plugged in: {batt.power_plugged})\n"
                
        return info.strip()
    except Exception as e:
        return f"Failed to get system info: {str(e)}"

def initiate_lockdown() -> str:
    """
    Rapid-response security macro. Instantly mutes the system volume, 
    minimizes all open windows to the desktop, and locks the Windows workstation.
    """
    try:
        import ctypes
        import pyautogui
        
        # 1. Mute volume
        try:
            set_system_volume(0)
        except Exception:
            pass
            
        # 2. Minimize all windows (Win + D)
        pyautogui.hotkey('win', 'd')
        
        # 3. Lock Workstation
        ctypes.windll.user32.LockWorkStation()
        
        return "Lockdown Protocol initiated successfully. System muted, minimized, and locked."
    except Exception as e:
        return f"Lockdown failed: {str(e)}"
