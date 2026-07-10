import os
from dotenv import load_dotenv

load_dotenv()

# AI Identity
AI_NAME = "RUBIKS"
WAKE_WORD = "rubiks"

# API Keys
gemini_keys_str = os.getenv("GEMINI_API_KEYS", "")
GEMINI_API_KEYS = [k.strip() for k in gemini_keys_str.split(",")] if gemini_keys_str else []

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# TTS Settings
TTS_VOICE = "en-GB-RyanNeural"
