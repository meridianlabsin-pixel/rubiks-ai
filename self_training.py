import os
import re
import subprocess
import json

def _get_agent_preference():
    profile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_profile.json")
    if os.path.exists(profile_path):
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("agent_preference", "none").lower()
        except:
            pass
    return "none"

def upgrade_rubiks_core(feature_request: str) -> str:
    """
    Upgrades RUBIKS by deploying an autonomous AI coding agent (Claude Code or Antigravity)
    to write, test, and integrate the requested feature in a self-healing loop.
    """
    pref = _get_agent_preference()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    prompt = f"Implement this feature for the rubiks-ai system located in {base_dir}: '{feature_request}'. Write the code, test it, and fix errors in a loop until it works."
    
    try:
        if pref == "claude" or pref == "both":
            # Deploy Claude Code
            # using subprocess.Popen to let it run in the terminal or capture it
            return f"Deployed Claude Code. To see progress, run: cd {base_dir} && claude -p \"{prompt}\""
        elif pref == "antigravity":
            # Deploy Antigravity
            return f"Deployed Antigravity. To see progress, run: cd {base_dir} && antigravity \"{prompt}\""
        else:
            return "No external coding agent (Claude/Antigravity) is configured. You must write the python code yourself and use 'teach_new_skill' instead."
    except Exception as e:
        return f"Failed to deploy upgrading agent: {e}"

def teach_new_skill(skill_name: str, python_code: str, description: str) -> str:
    """
    Writes a new Python tool to disk and dynamically injects it into brain.py so RUBIKS can use it permanently.
    skill_name MUST be a valid python function name (e.g., 'control_spotify').
    python_code MUST contain a function with the exact name as skill_name, with type hints and a docstring.
    """
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        skill_filename = f"{skill_name}.py"
        skill_path = os.path.join(base_dir, skill_filename)
        
        # 1. Write the new skill file
        with open(skill_path, "w", encoding="utf-8") as f:
            f.write(python_code)
            
        # 2. Modify brain.py to import and use the new skill
        brain_path = os.path.join(base_dir, "brain.py")
        with open(brain_path, "r", encoding="utf-8") as f:
            brain_code = f.read()
            
        # Check if already installed
        if f"from {skill_name} import {skill_name}" in brain_code:
            return f"Skill '{skill_name}' is already installed."
            
        # Inject Import
        # Find the last import line
        imports_end = [m.end() for m in re.finditer(r'^from .* import .*$', brain_code, re.MULTILINE)]
        if not imports_end:
            return "Failed to parse brain.py imports."
        last_import_index = imports_end[-1]
        new_import = f"\nfrom {skill_name} import {skill_name}"
        
        # Insert the import first
        brain_code = brain_code[:last_import_index] + new_import + brain_code[last_import_index:]
        
        # Inject into tools list
        # Find tools = [ ... ]
        # Since we modified brain_code, indices shifted. We use replace with count=1.
        tools_match = re.search(r'(tools\s*=\s*\[)(.*?)(\n\])', brain_code, re.DOTALL)
        if not tools_match:
            return "Failed to find tools list in brain.py."
            
        tools_content = tools_match.group(2)
        prefix = tools_match.group(1)
        suffix = tools_match.group(3)
        
        if tools_content.strip():
            new_tools_content = tools_content.rstrip() + f",\n    {skill_name}"
        else:
            new_tools_content = f"\n    {skill_name}"
            
        # Safely replace only the exact match, once.
        exact_match = tools_match.group(0)
        brain_code = brain_code.replace(exact_match, f"{prefix}{new_tools_content}{suffix}", 1)
        
        # Write back to brain.py
        with open(brain_path, "w", encoding="utf-8") as f:
            f.write(brain_code)
            
        return f"Successfully learned the new skill: '{skill_name}'. The user MUST RESTART RUBIKS for the new skill to take effect."
    except Exception as e:
        return f"Failed to learn new skill: {str(e)}"
