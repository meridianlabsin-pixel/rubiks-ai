# RUBIKS AI - Autonomous Desktop Agent

RUBIKS is a proto-AGI autonomous desktop assistant designed to operate your Windows PC natively. It comes with full PC vision, autonomous desktop tool execution, WhatsApp auto-replying, a terminal dashboard HUD, and a background "Autopilot Butler" mode.

## Features
- **Autopilot Butler**: Runs silently in the background, constantly taking screenshots of your PC to monitor for new WhatsApp or Discord messages. It will intelligently auto-reply on your behalf and save its actions to a `butler_log.txt`.
- **True Vision**: Uses Gemini 2.5 Flash Vision to see your screen and interact with it (clicking on UI elements, typing, etc.).
- **Swarm Mode**: Can spawn child agents (like ChatGPT or Claude) by physically opening your browser and typing prompts into them for complex tasks.
- **Dynamic Hot-Reloading**: Add new API keys via the terminal without restarting the system.
- **Self-Healing**: Gracefully catches rate limits (429 errors) and swaps to backup API keys seamlessly.

## Setup & Installation

1. **Install Requirements**
```bash
pip install -r requirements.txt
```

2. **API Keys**
Open `.env` and add your Gemini API keys:
```
GEMINI_API_KEYS="your_key_1,your_key_2"
```

3. **Run RUBIKS**
```bash
python main.py
```
Or simply double-click the `rubiks.bat` file.

## Privacy Note
All your personal data, chat history, and memory logs (`chat_memory.txt`, `butler_log.txt`, `user_profile.json`) are stored strictly **LOCALLY** on your hard drive. Nothing is uploaded to any cloud server except the queries sent directly to the Gemini API for processing. Your data is yours.
