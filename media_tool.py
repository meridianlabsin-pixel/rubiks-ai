import pyautogui

def control_media(action: str) -> str:
    """
    Controls global OS media playback (Spotify, YouTube, VLC, etc.).
    Valid actions: 'play', 'pause', 'next', 'previous', 'stop', 'mute'.
    """
    try:
        action = action.lower().strip()
        if action in ["play", "pause", "playpause", "toggle"]:
            pyautogui.press("playpause")
            return "Toggled media playback (Play/Pause)."
        elif action in ["next", "skip", "forward"]:
            pyautogui.press("nexttrack")
            return "Skipped to the next track."
        elif action in ["previous", "back", "prev"]:
            pyautogui.press("prevtrack")
            return "Went back to the previous track."
        elif action == "stop":
            pyautogui.press("stop")
            return "Stopped media playback."
        elif action in ["mute", "unmute"]:
            pyautogui.press("volumemute")
            return "Toggled system mute."
        else:
            return f"Unknown media action: '{action}'. Try 'play', 'pause', 'next', or 'previous'."
    except Exception as e:
        return f"Failed to control media: {str(e)}"
