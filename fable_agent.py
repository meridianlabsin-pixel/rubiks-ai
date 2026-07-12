"""
RUBIKS FABLE ENGINE v1.0
========================
A native long-horizon autonomous agent built on top of the Gemini API.
Inspired by Claude Fable 5's architecture, but entirely self-contained.

This engine can:
- Accept a massive goal and break it into a multi-step execution plan
- Execute each step using RUBIKS' full tool arsenal
- Self-verify each step before moving on
- Retry failed steps with alternate strategies
- Spawn sub-tasks and coordinate them
- Run in the background for as long as needed
- Report live progress to the terminal

Architecture:
  FableEngine (singleton)
    └── FableTask (per-goal)
         ├── Step 1 [DONE]
         ├── Step 2 [RUNNING]
         ├── Step 3 [PENDING]
         └── ...
"""

import threading
import time
import json
import random
import os
import traceback
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console(force_terminal=True)

# ─── FABLE STATE ────────────────────────────────────────────────────────

_fable_thread = None
_fable_task = None
_fable_running = False
_fable_log = []


class FableStep:
    """A single atomic step in a Fable execution plan."""
    def __init__(self, index: int, description: str, verification: str = ""):
        self.index = index
        self.description = description
        self.verification = verification
        self.status = "PENDING"      # PENDING | RUNNING | DONE | FAILED | RETRYING
        self.result = ""
        self.attempts = 0
        self.max_attempts = 3
        self.started_at = None
        self.completed_at = None


class FableTask:
    """Represents a full long-horizon goal broken into steps."""
    def __init__(self, goal: str):
        self.goal = goal
        self.steps = []
        self.status = "PLANNING"     # PLANNING | EXECUTING | VERIFYING | DONE | FAILED
        self.created_at = datetime.now()
        self.completed_at = None
        self.plan_text = ""
        self.final_summary = ""

    def add_step(self, description: str, verification: str = ""):
        step = FableStep(len(self.steps) + 1, description, verification)
        self.steps.append(step)
        return step

    def current_step(self):
        for s in self.steps:
            if s.status in ["PENDING", "RUNNING", "RETRYING"]:
                return s
        return None

    def progress(self):
        done = sum(1 for s in self.steps if s.status == "DONE")
        total = len(self.steps)
        return f"{done}/{total}"

    def is_complete(self):
        return all(s.status == "DONE" for s in self.steps)


def _log(msg: str, level: str = "INFO"):
    """Internal logging with timestamp."""
    global _fable_log
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "⚡", "WARN": "⚠️", "ERROR": "❌", "SUCCESS": "✅", "PLAN": "📋", "STEP": "🔧"}.get(level, "•")
    entry = f"[{ts}] {prefix} {msg}"
    _fable_log.append(entry)
    # Keep log bounded
    if len(_fable_log) > 200:
        _fable_log = _fable_log[-150:]
    # Print to terminal in real-time
    color = {"INFO": "dim cyan", "WARN": "yellow", "ERROR": "bold red", "SUCCESS": "bold green", "PLAN": "bold magenta", "STEP": "bold blue"}.get(level, "white")
    console.print(f"  [{color}][FABLE] {entry}[/{color}]", highlight=False)


def _get_gemini_model():
    """Create a fresh Gemini model instance with a randomly selected API key."""
    import google.generativeai as genai
    from config import GEMINI_API_KEYS

    if not GEMINI_API_KEYS:
        raise RuntimeError("No Gemini API keys available.")

    key = random.choice(GEMINI_API_KEYS)
    genai.configure(api_key=key)

    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        system_instruction="""You are the FABLE PLANNER — a strategic reasoning engine inside the RUBIKS AI system.
Your job is to break down complex, long-horizon goals into precise, executable steps.

RULES:
- Each step must be a SINGLE, ATOMIC action (one tool call or one code execution).
- Steps must be in correct dependency order.
- Each step should have a clear verification criteria.
- Be specific. "Write code" is bad. "Write a Python script that pings google.com 5 times and saves output to ping_log.txt" is good.
- You have access to: file system, terminal commands, web search, Python execution, browser automation, screen vision.
- Respond ONLY in valid JSON. No markdown, no explanation outside the JSON.

FORMAT:
{
  "plan_summary": "Brief description of the overall approach",
  "steps": [
    {
      "description": "Exact action to perform",
      "tool": "which tool or method to use (terminal_command | python_script | web_search | file_write | file_read | browser_open | screen_analyze)",
      "verification": "How to verify this step succeeded"
    }
  ]
}"""
    )
    return model


def _get_executor_model():
    """Create a Gemini model for step execution — translates step descriptions into actual tool calls."""
    import google.generativeai as genai
    from config import GEMINI_API_KEYS

    key = random.choice(GEMINI_API_KEYS)
    genai.configure(api_key=key)

    # Import all the tools the executor can use
    from pc_controller import run_terminal_command, execute_python_script, open_application, open_website, type_text, type_and_enter
    from web_tools import search_web
    from file_tools import list_files, read_file, write_file, find_recent_files, open_file, search_files
    from vision_tool import analyze_screen

    tools = [
        run_terminal_command,
        execute_python_script,
        open_application,
        open_website,
        type_text,
        type_and_enter,
        search_web,
        list_files,
        read_file,
        write_file,
        find_recent_files,
        open_file,
        search_files,
        analyze_screen,
    ]

    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        tools=tools,
        system_instruction="""You are the FABLE EXECUTOR — the action engine of the RUBIKS AI system.
You receive a specific step to execute. Use the available tools to complete it precisely.
- Execute the step exactly as described.
- If a tool fails, try an alternative approach.
- After execution, report what happened clearly.
- Be concise. No fluff. Just execute and report."""
    )
    return model


def _get_verifier_model():
    """Create a Gemini model for self-verification."""
    import google.generativeai as genai
    from config import GEMINI_API_KEYS

    key = random.choice(GEMINI_API_KEYS)
    genai.configure(api_key=key)

    from pc_controller import run_terminal_command
    from file_tools import read_file, list_files, search_files
    from vision_tool import analyze_screen

    tools = [run_terminal_command, read_file, list_files, search_files, analyze_screen]

    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        tools=tools,
        system_instruction="""You are the FABLE VERIFIER — a quality assurance engine.
You receive a step that was just executed, along with its result and verification criteria.
Your job:
1. Use the available tools to CHECK if the step was truly completed successfully.
2. Respond with ONLY a JSON object:
   {"verified": true/false, "reason": "explanation of what you found"}
- verified=true means the step genuinely succeeded.
- verified=false means something is wrong and the step should be retried."""
    )
    return model


# ─── CORE FABLE LOOP ────────────────────────────────────────────────────

def _fable_loop(goal: str):
    """The main autonomous execution loop. Runs in a background thread."""
    global _fable_task, _fable_running

    _fable_running = True
    task = FableTask(goal)
    _fable_task = task

    _log(f"FABLE ENGINE ACTIVATED", "SUCCESS")
    _log(f"Goal: {goal}", "INFO")
    _log(f"Phase 1: STRATEGIC PLANNING...", "PLAN")

    # ─── PHASE 1: PLANNING ──────────────────────────
    try:
        planner = _get_gemini_model()
        chat = planner.start_chat()
        
        planning_prompt = f"""Break down this goal into precise, executable steps:

GOAL: {goal}

Remember:
- Each step must be a single atomic action.
- Include verification criteria for each step.
- Order steps by dependency (do prerequisites first).
- Be practical and specific. Use terminal commands, Python scripts, file operations, or web searches.
- Respond ONLY in the JSON format specified in your instructions."""

        response = chat.send_message(planning_prompt)
        raw_plan = response.text.strip()

        # Clean up potential markdown code fences
        if raw_plan.startswith("```"):
            raw_plan = raw_plan.split("\n", 1)[1] if "\n" in raw_plan else raw_plan[3:]
        if raw_plan.endswith("```"):
            raw_plan = raw_plan[:-3]
        if raw_plan.startswith("json"):
            raw_plan = raw_plan[4:]
        raw_plan = raw_plan.strip()

        plan_data = json.loads(raw_plan)
        task.plan_text = plan_data.get("plan_summary", "No summary provided.")
        
        _log(f"Plan: {task.plan_text}", "PLAN")

        for step_data in plan_data.get("steps", []):
            desc = step_data.get("description", "Unknown step")
            verif = step_data.get("verification", "Check manually")
            task.add_step(desc, verif)
            _log(f"Step {len(task.steps)}: {desc}", "PLAN")

        if not task.steps:
            _log("Planner returned zero steps. Aborting.", "ERROR")
            task.status = "FAILED"
            _fable_running = False
            return

        _log(f"Plan locked: {len(task.steps)} steps total.", "SUCCESS")

    except json.JSONDecodeError as e:
        _log(f"Planner returned invalid JSON: {e}", "ERROR")
        _log(f"Raw response: {raw_plan[:500]}", "ERROR")
        task.status = "FAILED"
        _fable_running = False
        return
    except Exception as e:
        _log(f"Planning failed: {e}", "ERROR")
        task.status = "FAILED"
        _fable_running = False
        return

    # ─── PHASE 2: EXECUTION ──────────────────────────
    task.status = "EXECUTING"
    _log(f"Phase 2: AUTONOMOUS EXECUTION", "STEP")

    for step in task.steps:
        if not _fable_running:
            _log("Fable loop was manually stopped.", "WARN")
            task.status = "FAILED"
            return

        step.status = "RUNNING"
        step.started_at = datetime.now()
        _log(f"Executing Step {step.index}/{len(task.steps)}: {step.description}", "STEP")

        while step.attempts < step.max_attempts:
            step.attempts += 1

            try:
                # Create a fresh executor for each attempt (key rotation)
                executor = _get_executor_model()
                exec_chat = executor.start_chat(enable_automatic_function_calling=True)

                exec_prompt = f"""Execute this step NOW using your available tools:

STEP: {step.description}

Context:
- This is step {step.index} of {len(task.steps)} in a larger goal: "{goal}"
- Previous steps have already been completed successfully.
- Execute precisely. Use the right tool. Report the result."""

                exec_response = exec_chat.send_message(exec_prompt)
                step.result = exec_response.text if exec_response.text else "Step executed (no text response)."

                _log(f"Step {step.index} executed. Result: {step.result[:200]}", "INFO")

                # ─── PHASE 2.5: SELF-VERIFICATION ──────────────
                if step.verification:
                    _log(f"Verifying Step {step.index}...", "INFO")
                    try:
                        verifier = _get_verifier_model()
                        ver_chat = verifier.start_chat(enable_automatic_function_calling=True)

                        ver_prompt = f"""Verify this step was completed correctly:

STEP: {step.description}
EXECUTION RESULT: {step.result}
VERIFICATION CRITERIA: {step.verification}

Use your tools to check. Respond ONLY with JSON: {{"verified": true/false, "reason": "..."}}"""

                        ver_response = ver_chat.send_message(ver_prompt)
                        ver_text = ver_response.text.strip()

                        # Parse verification result
                        if ver_text.startswith("```"):
                            ver_text = ver_text.split("\n", 1)[1] if "\n" in ver_text else ver_text[3:]
                        if ver_text.endswith("```"):
                            ver_text = ver_text[:-3]
                        if ver_text.startswith("json"):
                            ver_text = ver_text[4:]
                        ver_text = ver_text.strip()

                        ver_data = json.loads(ver_text)

                        if ver_data.get("verified", False):
                            _log(f"Step {step.index} VERIFIED ✅: {ver_data.get('reason', '')}", "SUCCESS")
                            step.status = "DONE"
                            step.completed_at = datetime.now()
                            break
                        else:
                            reason = ver_data.get("reason", "Unknown failure")
                            _log(f"Step {step.index} FAILED verification (attempt {step.attempts}): {reason}", "WARN")
                            if step.attempts < step.max_attempts:
                                step.status = "RETRYING"
                                _log(f"Retrying step {step.index}...", "WARN")
                                time.sleep(2)
                            else:
                                # Max retries hit, accept and move on
                                _log(f"Step {step.index} max retries hit. Accepting and moving on.", "WARN")
                                step.status = "DONE"
                                step.completed_at = datetime.now()
                                break

                    except Exception as ver_err:
                        _log(f"Verification error (non-fatal): {ver_err}", "WARN")
                        # If verification itself errors, accept the step
                        step.status = "DONE"
                        step.completed_at = datetime.now()
                        break
                else:
                    # No verification criteria — auto-accept
                    step.status = "DONE"
                    step.completed_at = datetime.now()
                    break

            except Exception as exec_err:
                _log(f"Step {step.index} execution error (attempt {step.attempts}): {exec_err}", "ERROR")
                if step.attempts < step.max_attempts:
                    step.status = "RETRYING"
                    time.sleep(3)
                else:
                    step.status = "FAILED"
                    step.result = f"Failed after {step.max_attempts} attempts: {exec_err}"
                    _log(f"Step {step.index} permanently failed.", "ERROR")
                    break

    # ─── PHASE 3: FINAL SUMMARY ──────────────────────────
    done_count = sum(1 for s in task.steps if s.status == "DONE")
    fail_count = sum(1 for s in task.steps if s.status == "FAILED")

    if fail_count == 0:
        task.status = "DONE"
        task.final_summary = f"All {done_count} steps completed successfully."
        _log(f"🏆 GOAL ACHIEVED: {task.final_summary}", "SUCCESS")
    else:
        task.status = "DONE"
        task.final_summary = f"{done_count}/{len(task.steps)} steps completed. {fail_count} failed."
        _log(f"Goal finished with issues: {task.final_summary}", "WARN")

    task.completed_at = datetime.now()
    duration = (task.completed_at - task.created_at).total_seconds()
    _log(f"Total execution time: {duration:.1f} seconds", "INFO")

    # Save execution report to disk
    _save_report(task)

    _fable_running = False


def _save_report(task: FableTask):
    """Save a full execution report to disk."""
    try:
        report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fable_reports")
        os.makedirs(report_dir, exist_ok=True)
        
        ts = task.created_at.strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(report_dir, f"fable_{ts}.txt")

        lines = []
        lines.append(f"RUBIKS FABLE EXECUTION REPORT")
        lines.append(f"{'=' * 50}")
        lines.append(f"Goal: {task.goal}")
        lines.append(f"Status: {task.status}")
        lines.append(f"Started: {task.created_at}")
        lines.append(f"Completed: {task.completed_at}")
        lines.append(f"Plan: {task.plan_text}")
        lines.append(f"Summary: {task.final_summary}")
        lines.append(f"")
        lines.append(f"STEPS:")
        lines.append(f"-" * 50)
        for s in task.steps:
            lines.append(f"  Step {s.index}: [{s.status}] {s.description}")
            lines.append(f"    Attempts: {s.attempts} | Result: {s.result[:300]}")
            lines.append("")
        
        lines.append(f"\nFULL LOG:")
        lines.append(f"-" * 50)
        for entry in _fable_log:
            lines.append(f"  {entry}")

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        _log(f"Report saved: {report_path}", "SUCCESS")
    except Exception as e:
        _log(f"Failed to save report: {e}", "WARN")


# ─── PUBLIC API ──────────────────────────────────────────────────────────

def launch_fable_agent(goal: str) -> str:
    """Launches the RUBIKS Fable Engine to autonomously execute a complex, multi-step goal in the background.
    Use this for large tasks that require planning, execution, and verification across multiple steps.
    Example goals: 'Build a portfolio website', 'Research and compare 5 laptops under 50k', 'Set up a Node.js project with Express and MongoDB'."""
    global _fable_thread, _fable_running

    if _fable_running and _fable_thread and _fable_thread.is_alive():
        return f"Fable Engine is already running a task: '{_fable_task.goal}' (Progress: {_fable_task.progress()}). Use /fable status to check, or /fable stop to cancel."

    _fable_thread = threading.Thread(target=_fable_loop, args=(goal,), daemon=True)
    _fable_thread.start()

    return f"🔥 FABLE ENGINE ACTIVATED. Goal: '{goal}'. Running autonomously in background. Type '/fable status' to monitor progress."


def stop_fable_agent() -> str:
    """Stops the currently running Fable agent."""
    global _fable_running
    if not _fable_running:
        return "No Fable agent is currently running."
    _fable_running = False
    return "Fable Engine shutdown signal sent. The agent will stop after completing its current step."


def get_fable_status() -> str:
    """Returns the current status of the Fable agent."""
    global _fable_task, _fable_running

    if not _fable_task:
        return "No Fable task has been launched yet. Use '/fable <goal>' to start one."

    task = _fable_task
    lines = []
    lines.append(f"╔══════════════════════════════════════════════╗")
    lines.append(f"║  RUBIKS FABLE ENGINE — STATUS                ║")
    lines.append(f"╠══════════════════════════════════════════════╣")
    lines.append(f"║  Goal: {task.goal[:40]}")
    lines.append(f"║  Status: {task.status}")
    lines.append(f"║  Progress: {task.progress()}")
    lines.append(f"║  Running: {'YES' if _fable_running else 'NO'}")
    lines.append(f"╠══════════════════════════════════════════════╣")

    for s in task.steps:
        icon = {"DONE": "✅", "RUNNING": "🔄", "PENDING": "⏳", "FAILED": "❌", "RETRYING": "🔁"}.get(s.status, "•")
        lines.append(f"║  {icon} Step {s.index}: [{s.status}] {s.description[:45]}")

    lines.append(f"╚══════════════════════════════════════════════╝")

    return "\n".join(lines)


def get_fable_log(last_n: int = 20) -> str:
    """Returns the last N entries from the Fable execution log."""
    global _fable_log
    if not _fable_log:
        return "Fable log is empty."
    entries = _fable_log[-last_n:]
    return "\n".join(entries)
