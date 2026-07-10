import os
import time
import warnings
warnings.filterwarnings("ignore")

def generate_image(prompt: str, style: str = "photorealistic") -> str:
    """
    Generates a visual image based on a textual prompt and saves it to the Desktop.
    Cascades through multiple free providers until one works.
    It automatically opens the image for the user to see.
    """
    desktop_path = os.path.expanduser("~/Desktop")
    seed = int(time.time())
    safe_name = "".join(c for c in prompt[:25] if c.isalnum() or c == ' ').strip().replace(' ', '_')
    if not safe_name:
        safe_name = "rubiks_image"
    file_path = os.path.join(desktop_path, f"{safe_name}_{seed}.png")

    full_prompt = f"{prompt}, {style} style" if style else prompt
    errors = []

    # --- Provider 1: Gemini native image generation (cycles through all keys) ---
    try:
        from google import genai
        from google.genai import types
        from dotenv import load_dotenv
        load_dotenv(override=True)
        gemini_keys_str = os.environ.get("GEMINI_API_KEYS", "")
        fresh_keys = [k.strip() for k in gemini_keys_str.split(",")] if gemini_keys_str else []
        
        for key in fresh_keys:
            try:
                client = genai.Client(api_key=key)
                response = client.models.generate_content(
                    model='gemini-2.5-flash-image',
                    contents=f'Generate an image: {full_prompt}. Only output the image, no text.',
                    config=types.GenerateContentConfig(response_modalities=['IMAGE'])
                )
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data and part.inline_data.data:
                        with open(file_path, 'wb') as f:
                            f.write(part.inline_data.data)
                        os.startfile(file_path)
                        return f"Image generated and saved to Desktop: {os.path.basename(file_path)}"
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    continue  # Try next key
                errors.append(f"Gemini({key[:8]}...): {err_str[:80]}")
                continue
    except ImportError:
        errors.append("google-genai not installed")

    # --- Provider 2: Together AI free tier (Flux model) ---
    try:
        import urllib.request
        import urllib.parse
        import json
        
        together_url = "https://api.together.xyz/v1/images/generations"
        payload = json.dumps({
            "model": "black-forest-labs/FLUX.1-schnell-Free",
            "prompt": full_prompt,
            "width": 1024,
            "height": 1024,
            "n": 1
        })
        req = urllib.request.Request(
            together_url,
            data=payload.encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0',
                'Authorization': f'Bearer {os.environ.get("TOGETHER_API_KEY", "")}'
            }
        )
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read().decode())
        if result.get("data") and result["data"][0].get("url"):
            img_url = result["data"][0]["url"]
            urllib.request.urlretrieve(img_url, file_path)
            os.startfile(file_path)
            return f"Image generated via Flux and saved to Desktop: {os.path.basename(file_path)}"
    except Exception as e:
        errors.append(f"Together: {str(e)[:80]}")

    # --- Provider 3: Use the Swarm to deploy ChatGPT for DALL-E ---
    try:
        from swarm_tool import execute_swarm
        swarm_payload = json.dumps([{"ai": "chatgpt", "task": f"Generate this image using DALL-E: {prompt}. Style: {style}. Download the result."}])
        swarm_result = execute_swarm(swarm_payload)
        if "error" in str(swarm_result).lower() or "limit" in str(swarm_result).lower():
            return f"ChatGPT's DALL-E image limit hit. All free image providers are currently exhausted. Try again in a few minutes, Boss."
        return f"Swarm deployed to ChatGPT for image generation. Check your browser tab."
    except Exception as e:
        errors.append(f"Swarm: {str(e)[:80]}")

    # --- All providers failed ---
    error_summary = " | ".join(errors) if errors else "Unknown error"
    return f"All image generation providers failed. Errors: {error_summary}"
