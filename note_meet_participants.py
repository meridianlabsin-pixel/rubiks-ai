import datetime
import os
from vision_tool import analyze_screen

def note_meet_participants() -> str:
    """
    Detects active Google Meet participants on screen and saves their names to a log file.
    """
    try:
        # 1. Analyze the screen for Google Meet participants
        participants_result = analyze_screen(
            question="Extract all visible names of participants from the active Google Meet window. If Google Meet is not active or no participants are visible, please state that."
        )

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry_header = f"\n--- Google Meet Participants Log Entry ({timestamp}) ---\n"
        log_entry_content = f"{participants_result}\n"
        full_log_entry = log_entry_header + log_entry_content

        file_name = "Google_Meet_Participants_Log.txt"
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
        
        # 3. Write the updated content back to the file
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(full_log_entry)
            
        return f"Participants noted and saved to '{file_name}'. Latest entry details: {participants_result}"
    except Exception as e:
        return f"Failed to note participants: {str(e)}"
