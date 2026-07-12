"""
Zero-Download Offline Executional Engine
========================================
This replaces the heavy HuggingFace Transformers model.
It uses instantaneous NLP heuristics (Regex/Keyword matching)
to route natural language commands directly to the physical tools.
Requires 0 GB of downloads, 0 API cost, and executes instantly offline.
"""

import re
import random
from config import AI_NAME
from rich.console import Console

# Import all tools
from pc_controller import get_system_stats, open_application, run_terminal_command
from web_tools import search_web
from youtube_tool import play_on_youtube
from whatsapp_tool import send_whatsapp_message
from memory_tool import remember_fact, recall_memories
from briefing_tool import get_morning_briefing
from email_tool import check_emails

console = Console(force_terminal=True)

class LocalBrain:
    def __init__(self):
        console.print(f"\n[bold yellow][System] Protocol Omega (Local Backup) Initialized.[/bold yellow]")
        console.print(f"[bold green][System] Offline Executional Engine Online! 0 GB Download required.[/bold green]\n")

    def send_message(self, text: str) -> str:
        cmd = text.lower().strip()
        
        # ─── EXECUTIONAL INTENT MATCHING ───

        # 1. Email Checking
        if any(kw in cmd for kw in ["email", "e-mail", "inbox", "mail"]):
            return "Checking your emails offline...\n\n" + check_emails()

        # 2. System Stats
        if any(kw in cmd for kw in ["system stat", "cpu", "ram", "battery", "performance", "how is my pc"]):
            return "Fetching offline system stats...\n\n" + get_system_stats()

        # 3. Morning Briefing / Weather / Time
        if any(kw in cmd for kw in ["morning", "briefing", "weather", "time", "date"]):
            return "Generating your offline briefing...\n\n" + get_morning_briefing()

        # 4. WhatsApp Messaging
        m_whatsapp = re.search(r'(?:text|whatsapp|message)\s+(\w+)\s+(?:saying|that)\s+(.*)', cmd)
        if m_whatsapp:
            target = m_whatsapp.group(1)
            msg = m_whatsapp.group(2)
            res = send_whatsapp_message(target, msg)
            return f"Executing offline WhatsApp protocol: {res}"

        # 5. Application Opening
        m_open = re.search(r'open\s+(.*)', cmd)
        if m_open:
            app = m_open.group(1)
            res = open_application(app)
            return f"Opening {app} offline: {res}"

        # 6. Web Searching
        m_search = re.search(r'(?:search|google|look up)\s+(.*)', cmd)
        if m_search:
            query = m_search.group(1).replace("for ", "")
            res = search_web(query)
            return f"Searching the web for {query} offline: {res}"

        # 7. Media Playing
        m_play = re.search(r'play\s+(.*)', cmd)
        if m_play:
            song = m_play.group(1)
            res = play_on_youtube(song)
            return f"Playing {song} on YouTube offline: {res}"

        # 8. Memory: Recall
        if any(kw in cmd for kw in ["what do you remember", "what are my memories", "tell me what you know"]):
            return "Recalling offline memory banks...\n\n" + recall_memories()

        # 9. Memory: Store
        m_remember = re.search(r'remember\s+(?:that\s+)?(.*)', cmd)
        if m_remember:
            fact = m_remember.group(1)
            res = remember_fact(fact)
            return f"Fact stored securely in offline memory: {res}"

        # ─── CONVERSATIONAL FALLBACKS ───
        
        greetings = ["hello", "hi", "hey", "greetings", "good evening", "good afternoon"]
        if any(cmd.startswith(g) for g in greetings):
            return f"Hello, Boss. I am operating entirely offline."

        if "who are you" in cmd:
            return f"I am {AI_NAME}. I am currently offline."

        if "thank" in cmd:
            responses = ["Acknowledged.", "Done.", "Sir."]
            return random.choice(responses)

        # Catch-all
        return "I am disconnected from the cloud. I can check emails, stats, weather, open apps, send messages, and recall memories locally. What do you need, Boss?"
