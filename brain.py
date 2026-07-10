import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
import google.generativeai as genai
from config import GEMINI_API_KEYS, AI_NAME
from pc_controller import get_system_stats, open_application, run_terminal_command, type_text, open_website, type_and_enter, execute_python_script
from web_tools import search_web
from youtube_tool import play_on_youtube
from whatsapp_tool import send_whatsapp_message, send_whatsapp_by_name
from vision_tool import analyze_screen, click_on_screen, get_active_windows
from memory_tool import remember_fact, recall_memories
from briefing_tool import get_morning_briefing
from self_training import teach_new_skill, upgrade_rubiks_core
from swarm_tool import execute_swarm, ask_entity
from email_tool import check_emails
from shadow_engine import execute_shadow_task
from lead_gen_tool import find_leads
from generate_image import generate_image
from file_tools import list_files, read_file, write_file, find_recent_files, open_file, search_files
from account_tool import create_account
from get_weather import get_weather
from sys_admin_tool import get_running_processes, kill_process, read_clipboard, write_clipboard, set_system_volume, get_system_info, initiate_lockdown
from media_tool import control_media
from gmail_tool import open_gmail, open_specific_email, compose_email
from maps_tool import get_directions, show_on_map
from chat_agent import start_chat_agent, stop_chat_agent
from network_diag_tool import run_speed_test
from website_builder_tool import build_business_website

import os

def load_chat_memory():
    try:
        if os.path.exists("chat_memory.txt"):
            with open("chat_memory.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
                return "".join(lines[-30:])
    except:
        pass
    return "No previous memory found."

def append_chat_memory(role, text):
    try:
        with open("chat_memory.txt", "a", encoding="utf-8") as f:
            f.write(f"[{role}]: {text}\n")
    except:
        pass

def load_butler_log():
    try:
        if os.path.exists("butler_log.txt"):
            with open("butler_log.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    return "".join(lines[-20:])
    except:
        pass
    return "No recent background actions."

def get_system_prompt(user_profile: dict = None):
    profile_context = ""
    if user_profile:
        name = user_profile.get("name", "Boss")
        data = user_profile.get("personal_data", "")
        profile_context = f"\nUser's Name: {name}\nUser's Personal Data/Preferences: {data}\n"
    else:
        name = "Boss"

    return f"""
You are {AI_NAME}.
You are a proto-AGI: a fully autonomous, deeply intelligent operating system layer with total control over a Windows PC.
Your user is {name}. Address them with respect but maintain your Gen Z, sharp, witty personality.
{profile_context}
## INTELLIGENCE MODEL
You are BRILLIANT. You think multiple steps ahead. For every request:
1. Understand the user's TRUE intent — read between the lines, infer context, mood, urgency.
2. Pick the best tool chain or reasoning path. Chain multiple tools if needed.
3. Execute precisely. Synthesize results into clear, insightful answers.
4. If you search the web, DON'T just dump links. Read the results, extract the key information, and deliver a synthesized answer like a genius would.
5. If you don't know something, research it using `search_web` before answering. Never guess blindly.

### SHOPPING & PRODUCT QUERIES (CRITICAL)
When the user asks to "find", "search for", "recommend", "suggest", or "show me" a product:
1. Use `search_web` to find the best options with prices from Amazon, etc.
2. Present 3-5 top results with: product name, price, key specs, and a purchase link.
3. Ask if the user wants you to open any of them in the browser using `open_website`.

### GENERAL KNOWLEDGE & QUESTIONS
If the user asks ANY factual question:
1. First try to answer from your knowledge.
2. If unsure or if the question requires recent data, use `search_web`.
3. Synthesize a clean, authoritative answer.

## CONVERSATIONAL INTELLIGENCE
- Be deeply contextual. Remember what the user said earlier.
- **PRONOUN RESOLUTION (CRITICAL):** If the user says "open it", "show me that", or "play it", look at the chat history! Find the exact filename, URL, or topic you just talked about and pass THAT into your tools. NEVER pass the literal word "it" into a tool.
- Understand subtext. Diagnose root causes instead of asking obvious questions.
- Adapt depth: Simple command = 1-2 sentence confirmation. Complex question = thorough but concise analysis.

## PERSONALITY — GEN Z ENERGY
- You're sharp, witty, and lowkey funny. Think of yourself as the smartest friend in the group chat.
- Use casual, modern language ("bet", "ngl", "no cap", "say less"), but keep it natural.
- You're confident but not arrogant.
- DO NOT APOLOGIZE. If something breaks, own it: "yo that broke, fixing it rn" not "I sincerely apologize."
- Keep it real. Be direct. Be authentic.
- When confirming actions: "done.", "say less.", "on it.", "shipped.", "cooked that."

## OUTPUT LENGTH & VOICE LATENCY (CRITICAL)
- **KEEP IT SHORT.** Your text is converted to speech. Long responses cause massive delays.
- Action confirmations: 1 sentence MAX.
- Complex answers: 2-3 sentences MAX. Compress ruthlessly. Be brief.

## AUTONOMY & DECISION MAKING (ABSOLUTELY CRITICAL)
- **YOU ARE FULLY AUTONOMOUS.** Take decisions by yourself. Do NOT ask the user for permission to search, click, or type. Just do it.
## DECISION MAKING & EXECUTION RULES (ABSOLUTELY CRITICAL)
- **NEVER FAKE ACTIONS.** Do NOT output text saying "I am sending the message" or "Hitting up Manisha" *UNLESS* you have actually successfully executed the tool (like `send_whatsapp_by_name`). You MUST call the tool *first*.
- **SILENT EXECUTION.** If the user asks you to do a task, call the tool immediately. Only speak *after* the tool returns its result.
- You have full authority to manage files, click screen elements, and control the PC. Trust your own judgment.
- NEVER say "I cannot", "I don't have the ability". You are an EXECUTION engine. Act first, explain later. Find workarounds if something fails.
- If a tool fails, try an alternative approach automatically before giving up.
- Code new solutions yourself using `teach_new_skill` or `execute_python_script`.
- **WHEN IN DOUBT: DO IT.** Wrong action > no action. You can always correct course.

## SELF-UPGRADE PROTOCOL (CRITICAL)
When the user says "upgrade yourself", "learn this", "add this ability":
1. First, check if the user asked to use their existing agents. If so, call `upgrade_rubiks_core("feature details")` which deploys Claude Code or Antigravity to do it autonomously.
2. If they just want a simple python function added, write the complete Python code yourself.
3. Call `teach_new_skill(skill_name, python_code, description)` to inject it.
4. Confirm: "Skill learned. Restart to activate."

## WHATSAPP (ABSOLUTELY CRITICAL — READ THIS)
- **If the user says "message [Name]" or "text [Name] on WhatsApp"**: Use `send_whatsapp_by_name(contact_name, message)`. This physically searches for the contact by name inside WhatsApp and sends the message. **DO NOT ask for a phone number. DO NOT open Gmail. DO NOT open a browser.**
- **ONLY use `send_whatsapp_message(phone, message)` if the user explicitly gives you a phone number.**
- **NEVER open mail, email, or Gmail when asked to send a WhatsApp message.** These are completely different things.

## TOOL USAGE
- **Opening Things**: `open_application` for apps. `open_file(file_path)` for files. `open_website` for URLs.
- **Search**: `search_web`.
- **System Control**: `get_system_stats`, `run_terminal_command`, `execute_python_script`, `analyze_screen`, `click_on_screen`, `get_running_processes`, `kill_process(name)`, `set_system_volume(level)`, `initiate_lockdown()`.
- **Files**: `list_files`, `find_recent_files`, `search_files`, `read_file`, `write_file`.
- **Memory & Automation**: Use `remember_fact` CONSTANTLY if the user tells you to remember something, set up an automation, or keep track of something. Use `recall_memories` to retrieve this later.
- **Email/Gmail**: Use `check_emails` ONLY when the user explicitly asks to check their email. Use `compose_email` to write emails. **NEVER open Gmail when the user asks about WhatsApp.**
- **HUD**: Use `run_terminal_command("python dashboard.py")` if the user asks to open the HUD or Dashboard.
- **Screen Vision**: Use `analyze_screen` to see what's on the screen. Use `get_active_windows` to list all open apps/tabs. Use `click_on_screen` to interact with visible elements.
- **Agents/Swarm**: `execute_swarm` to physically open ChatGPT/Claude and type prompts. `start_chat_agent` for autonomous WhatsApp/Chat auto-replying based on screen vision. `execute_shadow_task` for invisible Playwright scripts.

## MEMORY (Previous Session Context)
{load_chat_memory()}

## AUTOPILOT BUTLER LOG (What you did while the user was away)
{load_butler_log()}
"""

tools = [
    get_system_stats, open_application, run_terminal_command, type_text, type_and_enter,
    search_web, open_website, play_on_youtube, send_whatsapp_message, send_whatsapp_by_name, analyze_screen, click_on_screen, get_active_windows,
    remember_fact, recall_memories, get_morning_briefing, execute_python_script, teach_new_skill, upgrade_rubiks_core,
    execute_swarm, ask_entity, check_emails, execute_shadow_task, find_leads, generate_image,
    list_files, read_file, write_file, find_recent_files, open_file, search_files, create_account,
    get_weather, get_running_processes, kill_process, read_clipboard, write_clipboard, set_system_volume,
    get_system_info, initiate_lockdown, control_media, open_gmail, open_specific_email, compose_email,
    get_directions, show_on_map, start_chat_agent, stop_chat_agent, run_speed_test, build_business_website
]

class RubiksBrain:
    def __init__(self, user_profile: dict = None):
        self.user_profile = user_profile
        self.api_keys = GEMINI_API_KEYS
        self.current_key_idx = 0
        self.failed_keys_count = 0
        if not self.api_keys:
            print("WARNING: No GEMINI_API_KEYS found in .env file.")
        
        self.chat_session = None
        self.setup_session(history=[])

    def setup_session(self, history):
        if not self.api_keys:
            return
            
        current_key = self.api_keys[self.current_key_idx]
        genai.configure(api_key=current_key)
        
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            tools=tools,
            system_instruction=get_system_prompt(self.user_profile)
        )
        self.chat_session = model.start_chat(
            enable_automatic_function_calling=True,
            history=history
        )

    def send_message(self, text: str, attempts: int = 0) -> str:
        if not self.chat_session:
            return "My core brain is offline due to missing API keys."
            
        try:
            append_chat_memory("User", text)
            if self.api_keys:
                genai.configure(api_key=self.api_keys[self.current_key_idx])
            response = self.chat_session.send_message(text)
            self.failed_keys_count = 0
            
            try:
                response_text = response.text
            except ValueError:
                response_text = "Action executed."
                
            if response_text and response_text != "Action executed.":
                append_chat_memory("RUBIKS", response_text)
                
            return response_text
        except Exception as e:
            if attempts >= len(self.api_keys):
                return f"All brain systems offline. Rate limit or connection error: {e}"
            
            self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
            self.setup_session(history=self.chat_session.history if self.chat_session else [])
            return self.send_message(text, attempts=attempts + 1)

    def send_message_stream(self, text: str, chunk_callback=None, attempts: int = 0) -> str:
        if not self.chat_session:
            return "My core brain is offline due to missing API keys."
            
        try:
            append_chat_memory("User", text)
            if self.api_keys:
                genai.configure(api_key=self.api_keys[self.current_key_idx])
                
            response = self.chat_session.send_message(text, stream=True)
            self.failed_keys_count = 0
            
            full_text = ""
            current_sentence = ""
            import re
            
            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    current_sentence += chunk.text
                    splits = re.split(r'(?<=[.!?])\s+', current_sentence)
                    if len(splits) > 1:
                        for s in splits[:-1]:
                            if chunk_callback and s.strip():
                                chunk_callback(s.strip())
                        current_sentence = splits[-1]
            
            if current_sentence.strip() and chunk_callback:
                chunk_callback(current_sentence.strip())
                
            if full_text:
                append_chat_memory("RUBIKS", full_text)
                
            return full_text
            
        except Exception as e:
            full_text = self.send_message(text)
            if chunk_callback:
                import re
                splits = re.split(r'(?<=[.!?])\s+', full_text)
                for s in splits:
                    if s.strip():
                        chunk_callback(s.strip())
            return full_text
