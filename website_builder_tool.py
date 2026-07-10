import os
from web_tools import search_web
import json
from swarm_tool import execute_swarm

def build_business_website(business_name: str, location: str) -> str:
    """Builds a website by searching for context, then deploying a Swarm agent to Claude to physically code it in the browser."""
    try:
        # 1. Search the web for real information
        query = f"{business_name} {location}"
        search_results = search_web(query)
        
        # 2. Build the ultra-detailed prompt
        prompt = f"""
You are an expert web developer and UI/UX designer.
I need a stunning, modern, single-page website for a business.

Business Name: {business_name}
Location: {location}

Context found online:
{search_results}

Requirements:
1. Output ONLY the raw HTML code in a single code block.
2. Use Tailwind CSS via CDN.
3. Include a beautiful Hero section, About Us, Services/Menu, and Contact/Footer.
4. Use Font Awesome for icons.
5. Use modern web design principles: glassmorphism, gradients, clean typography (import Google Fonts), and smooth hover effects.
6. Ensure it is fully responsive.
7. Inject the actual context found online into the website (e.g., real address, real services, real descriptions). If info is missing, use realistic placeholders.
8. Add some nice smooth scrolling or simple JS animations if possible.

Generate the code now.
"""
        
        # 3. Deploy to Claude via Swarm so the user sees it happen!
        swarm_payload = json.dumps([{"ai": "claude", "task": prompt}])
        result = execute_swarm(swarm_payload)
        
        return f"I have deployed a Swarm agent to Claude. It is now physically typing the website code in the browser! ({result})"
        
    except Exception as e:
        return f"Failed to deploy website swarm. Error: {str(e)}"
