import time
import sys
import os
import io

# Fix Windows terminal encoding
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.platform == "win32":
    os.system("chcp 65001 >nul 2>&1")
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import speech_recognition as sr
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
from rich.prompt import Prompt
from config import AI_NAME
from audio_engine import speak, list_microphones, stop_speaking, start_tts_engine, stream_speak
from brain import RubiksBrain
import threading
import psutil
import queue

console = Console(force_terminal=True)

# Queue for terminal input so we don't block
terminal_queue = queue.Queue()

def _terminal_input_thread():
    while True:
        try:
            line = Prompt.ask("\n[bold cyan][RUBIKS][/bold cyan] >")
            if line:
                terminal_queue.put(line)
        except Exception:
            pass

def start_terminal_thread():
    threading.Thread(target=_terminal_input_thread, daemon=True).start()

# ─── TERMINAL UI COMPONENTS ────────────────────────────────────────────

BANNER = r"""
  ____  _   _ ____ ___ _  ______
 |  _ \| | | | __ )_ _| |/ / ___|
 | |_) | | | |  _ \| || ' /\___ \
 |  _ <| |_| | |_) | || . \ ___) |
 |_| \_\\___/|____/___|_|\_\____/
"""

def show_banner():
    console.print(Panel(
        Text(BANNER, style="bold cyan", justify="center"),
        title="[bold white]AUTONOMOUS AI ASSISTANT[/bold white]",
        subtitle="[dim]v5.0 -- Swarm Commander Edition[/dim]",
        border_style="bright_cyan",
        box=box.DOUBLE_EDGE,
        padding=(0, 2),
    ))

def show_status(message: str, style: str = "bold green"):
    console.print(f"  [dim]>[/dim] [{style}]{message}[/{style}]")

def show_user(message: str, source: str):
    source_icon = "🎤" if source == "voice" else "⌨️"
    console.print(Panel(
        f"[bold white]{message}[/bold white]",
        title=f"[bold blue][ YOU | {source_icon} ][/bold blue]",
        border_style="blue",
        box=box.ROUNDED,
        padding=(0, 1),
    ))

def show_rubiks(message: str):
    console.print(Panel(
        f"[bold white]{message}[/bold white]",
        title="[bold magenta][ RUBIKS ][/bold magenta]",
        border_style="magenta",
        box=box.ROUNDED,
        padding=(0, 1),
    ))

def show_system(message: str):
    console.print(f"  [dim cyan]>> {message}[/dim cyan]")

def show_help():
    table = Table(
        title="[bold cyan]RUBIKS Commands[/bold cyan]",
        box=box.SIMPLE_HEAVY,
        border_style="cyan",
        show_header=True,
        header_style="bold white",
    )
    table.add_column("Command", style="bold yellow", min_width=20)
    table.add_column("Description", style="white")
    table.add_row("type anything", "Send a text command instantly")
    table.add_row("/voice", "Switch to Voice Mode")
    table.add_row("'switch to type mode'", "Say this in Voice Mode to go back to typing")
    table.add_row("/mics", "List all available microphones")
    table.add_row("/mic <number>", "Select a specific microphone")
    table.add_row("/key <api_key>", "Dynamically add a new Gemini API key to the system")
    table.add_row("/hud", "Launch the RUBIKS Dashboard HUD")
    table.add_row("/autopilot on", "Start the background Butler Mode (monitors screen/emails)")
    table.add_row("mute", "Immediately stops RUBIKS from speaking")
    table.add_row("[dim]Swarm Mode[/dim]", "[dim]Ask RUBIKS to do a complex task and it will spawn worker AIs[/dim]")
    table.add_row("stop", "Shut down RUBIKS")
    console.print(table)


# ─── MICROPHONE SELECTOR ───────────────────────────────────────────────

def select_microphone() -> int:
    mics = list_microphones()
    if not mics:
        console.print("[bold red]  No microphones detected![/bold red]")
        return None

    table = Table(
        title="[bold cyan]Available Microphones[/bold cyan]",
        box=box.ROUNDED,
        border_style="cyan",
    )
    table.add_column("#", style="bold yellow", justify="center", width=4)
    table.add_column("Microphone Name", style="white")

    for i, name in enumerate(mics):
        table.add_row(str(i), name)

    console.print(table)
    return None


# ─── PROACTIVE SYSTEM MONITOR ──────────────────────────────────────────

def system_monitor_loop(brain):
    """Continuously monitors system health in the background and proactively alerts the user if critical."""
    while True:
        try:
            time.sleep(30) # Check every 30 seconds
            cpu = psutil.cpu_percent(interval=1)
            batt = psutil.sensors_battery()
            
            alert_msg = None
            if cpu > 95:
                alert_msg = "SYSTEM ALERT: CPU usage is critically high above 95 percent. Warn the user immediately, but keep it brief."
            elif batt and batt.percent < 15 and not batt.power_plugged:
                alert_msg = f"SYSTEM ALERT: Battery is critically low at {batt.percent} percent. Warn the user immediately, but keep it brief."
                
            if alert_msg:
                # Trigger proactive thought
                reply_text = brain.send_message(alert_msg)
                print()
                show_system("Proactive Alert Triggered")
                show_rubiks(reply_text)
                try:
                    speak(reply_text)
                except Exception:
                    pass
                # Back off for 5 minutes after an alert so we don't spam
                time.sleep(300) 
        except Exception:
            time.sleep(60)

# ─── MAIN LOOP ─────────────────────────────────────────────────────────

def main():
    start_tts_engine()
    show_banner()
    show_status("Initializing RUBIKS Core Systems...")

    try:
        from config import GEMINI_API_KEYS
        if not GEMINI_API_KEYS:
            console.print("\n[bold yellow]No Gemini API Key found in .env![/bold yellow]")
            api_key = Prompt.ask("[bold cyan]Please paste your Gemini API Key here (or type 'skip' to exit)[/bold cyan]")
            if api_key and api_key.lower() != 'skip':
                env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
                with open(env_path, "a") as f:
                    f.write(f'\nGEMINI_API_KEYS="{api_key}"\n')
                os.environ["GEMINI_API_KEYS"] = api_key
                import config
                config.GEMINI_API_KEYS = [api_key]
                show_status("API Key saved! Implementing instantly...", "bold green")
                time.sleep(1)
            else:
                return

        from onboarding import run_onboarding
        user_profile = run_onboarding()

        brain = RubiksBrain(user_profile)
        show_status("Brain online -- Gemini connected.", "bold green")
    except Exception as e:
        console.print(f"[bold red]  Failed to initialize brain: {e}[/bold red]")
        return

    input_mode = "type"
    mic_index = None
    running = True

    # ─── WINDOWS STARTUP NOTIFICATION ─────────────────────────────
    try:
        from ctypes import windll
        windll.user32.MessageBeep(0x00000040)  # MB_ICONINFORMATION sound
    except Exception:
        pass

    show_status("Current Mode: TYPING", "bold yellow")
    console.print()
    show_help()
    console.print()

    # Greeting — time-based
    try:
        from greeting_engine import generate_greeting
        greeting = generate_greeting()
        show_rubiks(greeting)
        speak(greeting)
    except:
        pass
        
    # Start Proactive Monitor
    threading.Thread(target=system_monitor_loop, args=(brain,), daemon=True).start()

    # Setup Voice Recognizer once
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 400
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8
    recognizer.phrase_threshold = 0.3
    recognizer.non_speaking_duration = 0.4

    while running:
        try:
            # ─── TYPING MODE ───────────────────────────────────────
            if input_mode == "type":
                user_input = None
                
                try:
                    user_input = terminal_queue.get_nowait()
                except queue.Empty:
                    pass
                
                if not user_input or not user_input.strip():
                    time.sleep(0.1)
                    continue

                command = user_input.strip()
                cmd_lower = command.lower()
                source = "text"

                if cmd_lower == "/voice":
                    input_mode = "voice"
                    show_status("Switched to VOICE Mode. I am listening continuously.", "bold green")
                    continue
                    
                if cmd_lower == "/summon":
                    show_status("Summoning mini-RUBIKS chat agent...", "bold cyan")
                    import chat_agent
                    if chat_agent._chat_thread and chat_agent._chat_thread.is_alive():
                        show_system("Chat agent is already running! Type /dismiss to stop it.")
                    else:
                        res = chat_agent.start_chat_agent()
                        show_system(res)
                    continue
                    
                if cmd_lower == "/autopilot on":
                    import autopilot_agent
                    res = autopilot_agent.start_autopilot()
                    show_status(res, "bold green")
                    continue
                    
                if cmd_lower == "/autopilot off":
                    import autopilot_agent
                    res = autopilot_agent.stop_autopilot()
                    show_status(res, "bold yellow")
                    continue
                    
                if cmd_lower == "/hud":
                    show_status("Launching RUBIKS HUD Dashboard...", "bold cyan")
                    import dashboard
                    threading.Thread(target=dashboard.launch_dashboard, daemon=True).start()
                    continue
                    
                if cmd_lower == "/dismiss":
                    from chat_agent import stop_chat_agent
                    res = stop_chat_agent()
                    show_system(res)
                    continue

                if cmd_lower == "/mics":
                    select_microphone()
                    continue

                if cmd_lower.startswith("/mic "):
                    try:
                        idx = int(cmd_lower.split(" ")[1])
                        mics = list_microphones()
                        if 0 <= idx < len(mics):
                            mic_index = idx
                            show_status(f"Microphone set to: [{idx}] {mics[idx]}", "bold green")
                        else:
                            show_status("Invalid index.", "bold red")
                    except ValueError:
                        pass
                    continue
                
                if cmd_lower.startswith("/key "):
                    new_key = command.split(" ", 1)[1].strip()
                    if new_key:
                        if new_key not in brain.api_keys:
                            brain.api_keys.append(new_key)
                            env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
                            try:
                                lines = []
                                if os.path.exists(env_path):
                                    with open(env_path, "r") as f:
                                        lines = f.readlines()
                                
                                key_found = False
                                with open(env_path, "w") as f:
                                    for line in lines:
                                        if line.startswith("GEMINI_API_KEYS="):
                                            current_keys = line.strip().split("=", 1)[1].strip('"').strip("'")
                                            if current_keys and not current_keys.startswith("your_"):
                                                new_line = f'GEMINI_API_KEYS="{current_keys},{new_key}"\n'
                                            else:
                                                new_line = f'GEMINI_API_KEYS="{new_key}"\n'
                                            f.write(new_line)
                                            key_found = True
                                        else:
                                            f.write(line)
                                    if not key_found:
                                        f.write(f'GEMINI_API_KEYS="{new_key}"\n')
                                show_status("API Key successfully added to RUBIKS brain and saved!", "bold green")
                                if len(brain.api_keys) == 1:
                                    brain.setup_session([])
                            except Exception as e:
                                show_status(f"Failed to save key to .env: {e}", "bold red")
                        else:
                            show_status("Key already exists in brain.", "bold yellow")
                    else:
                        show_status("Usage: /key <your_api_key>", "bold red")
                    continue
                
                if cmd_lower in ["stop", "/stop", "exit", "/exit", "quit", "/quit"]:
                    farewell = "Shutting down all systems. Goodbye!"
                    show_rubiks(farewell)
                    try: speak(farewell)
                    except: pass
                    time.sleep(2)
                    running = False
                    break
                    
                if cmd_lower in ["mute", "(mute)", "stop speaking", "shh", "quiet"]:
                    stop_speaking()
                    show_status("Audio playback stopped.", "bold yellow")
                    continue

                if cmd_lower == "/help":
                    show_help()
                    continue

            # ─── VOICE MODE ────────────────────────────────────────
            elif input_mode == "voice":
                show_status("Listening... (Say 'switch to type mode' to go back to typing)", "bold yellow")
                
                command = ""
                source = "voice"
                
                try:
                    if mic_index is not None:
                        mic = sr.Microphone(device_index=mic_index)
                    else:
                        mic = sr.Microphone()
                        
                    with mic as mic_source:
                        recognizer.adjust_for_ambient_noise(mic_source, duration=0.5)
                        while input_mode == "voice":
                            try:
                                audio = recognizer.listen(mic_source, timeout=3, phrase_time_limit=20)
                                text = recognizer.recognize_google(audio).strip()
                                
                                if text:
                                    clean = text
                                    for prefix in ["rubik's ", "rubiks ", "rubik "]:
                                        if clean.lower().startswith(prefix):
                                            clean = clean[len(prefix):]
                                    command = clean if clean else text
                                    break
                            except sr.WaitTimeoutError:
                                pass
                            except sr.UnknownValueError:
                                pass
                except Exception as e:
                    show_status(f"Microphone error: {e}. Switching back to type mode.", "bold red")
                    input_mode = "type"
                    continue
                
                if not command:
                    continue
                
                cmd_lower = command.lower()
                
                if "switch to type mode" in cmd_lower or "/type" in cmd_lower:
                    input_mode = "type"
                    show_status("Switched to TYPING Mode.", "bold green")
                    continue
                    
                if "stop" in cmd_lower or "exit" in cmd_lower or "quit" in cmd_lower:
                    farewell = "Shutting down all systems. Goodbye!"
                    show_rubiks(farewell)
                    try: speak(farewell)
                    except: pass
                    time.sleep(2)
                    running = False
                    break
                    
                if cmd_lower in ["mute", "stop speaking", "shh", "quiet"]:
                    stop_speaking()
                    show_status("Audio playback stopped.", "bold yellow")
                    continue

            # ─── PROCESS THE COMMAND ─────────────────────────────
            
            # Interrupt: stop any ongoing speech immediately
            stop_speaking()
            
            print() 
            show_user(command, source)
            show_system("Processing...")

            cmd_lower = command.lower().strip()
            
            reply_text = brain.send_message_stream(command, chunk_callback=stream_speak)
            show_rubiks(reply_text)
            
            # Check if the Swarm Commander is waiting for user input
            try:
                from swarm_tool import check_swarm_question, provide_swarm_answer
                swarm_q = check_swarm_question()
                if swarm_q:
                    console.print(f"\n[bold yellow]  [Swarm Commander is asking YOU]: {swarm_q}[/bold yellow]")
                    swarm_answer = Prompt.ask("[bold cyan][YOUR ANSWER][/bold cyan] >")
                    provide_swarm_answer(swarm_answer)
            except Exception:
                pass

        except KeyboardInterrupt:
            print()
            farewell = "Emergency shutdown initiated. Goodbye."
            show_rubiks(farewell)
            os._exit(0)
        except Exception as e:
            console.print(f"  [bold red]Unexpected error: {e}[/bold red]")
            show_system("Recovering... please try again.")


if __name__ == "__main__":
    start_terminal_thread()
    main()
