import webbrowser
"""
R.U.B.I.K.S. Dashboard Launcher v11.0
Launches the Flask Bridge Server (for bidirectional Python <-> HTML communication)
and opens rubiks_hud.html in the default browser.
"""

import subprocess
import os
import threading
import time

RUBIKS_DIR = os.path.dirname(os.path.abspath(__file__))
HUD_PATH   = os.path.join(RUBIKS_DIR, "rubiks_hud.html")

# default browser executable path

def launch_dashboard():
    # 1. Start the Flask bridge server in a daemon thread
    try:
        from rubiks_bridge import run_bridge
        threading.Thread(target=run_bridge, daemon=True).start()
        # Give the server a moment to spin up
        time.sleep(1.0)
    except Exception as e:
        print(f"[HUD Error] Failed to start bridge server: {e}")

    # 2. Launch HTML HUD in the default browser (Comet)
    try:
        # os.startfile handles local HTML files much better on Windows and automatically uses the default browser.
        os.startfile(HUD_PATH)
    except Exception as e:
        print(f"[HUD Error] Failed to launch HUD: {e}")

    # Keep thread alive so the daemon threads keep running
    while True:
        time.sleep(60)

if __name__ == "__main__":
    launch_dashboard()
