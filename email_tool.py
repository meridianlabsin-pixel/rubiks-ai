"""
RUBIKS Email Tool
=================
Checks Gmail inbox by opening it directly in the browser.
Also provides a silent check mode for Autopilot that does NOT open a browser.
"""

def check_emails() -> str:
    """
    Checks the user's Gmail inbox by opening it directly in the browser.
    This avoids needing an App Password or IMAP configuration.
    """
    try:
        from gmail_tool import open_gmail
        open_gmail()
        return "I've opened your Gmail inbox in the browser so you can check your latest emails securely."
    except Exception as e:
        return f"Failed to open Gmail in browser: {str(e)}"

def check_emails_silent() -> str:
    """
    Silently checks for email notifications without opening a browser.
    Used by the Autopilot Butler to avoid disrupting the user.
    Returns info about any visible email notifications on screen.
    """
    try:
        from vision_tool import analyze_screen
        result = analyze_screen("Are there any email notifications, Gmail tabs, or email popups visible on the screen? If yes, summarize the sender and subject of any visible emails. If no emails are visible, say 'No email notifications visible.'")
        return result
    except Exception as e:
        return f"Silent email check failed: {str(e)}"
