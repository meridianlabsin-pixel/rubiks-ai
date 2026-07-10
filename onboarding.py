import os
import json
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()
PROFILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_profile.json")

def load_profile():
    if os.path.exists(PROFILE_PATH):
        try:
            with open(PROFILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def run_onboarding():
    profile = load_profile()
    if profile:
        return profile
        
    console.print(Panel("[bold cyan]Welcome to RUBIKS AI - First Boot Sequence[/bold cyan]\nI need some information to personalize your experience and set up my self-upgrading systems.", title="[bold white]INITIALIZATION[/bold white]", border_style="cyan"))
    
    name = Prompt.ask("[bold yellow]What is your name? (How should I address you?)[/bold yellow]")
    
    console.print("\n[dim]RUBIKS can physically write its own code to upgrade itself. To do this, it needs to know what AI coding agents you have installed on your terminal (e.g. Claude Code or Antigravity).[/dim]")
    agent_pref = Prompt.ask("[bold yellow]Do you use 'claude', 'antigravity', 'both', or 'none'?[/bold yellow]", choices=["claude", "antigravity", "both", "none"], default="none")
    
    personal_data = Prompt.ask("\n[bold yellow]Any other personal data I should remember forever? (e.g., 'I run a marketing agency', 'I hate Monday mornings', 'My favorite color is blue')[/bold yellow]")
    
    profile = {
        "name": name,
        "agent_preference": agent_pref,
        "personal_data": personal_data
    }
    
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=4)
        
    console.print("[bold green]\nProfile saved successfully! Booting core systems...[/bold green]\n")
    return profile
