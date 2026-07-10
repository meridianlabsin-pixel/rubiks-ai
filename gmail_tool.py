import webbrowser
"""
Gmail Tool - Opens and interacts with Gmail via Comet browser.

Provides functions to open Gmail inbox, search for specific emails,
and compose new emails with pre-filled fields.
"""

import subprocess
from urllib.parse import quote




def open_gmail() -> str:
    """Opens Gmail inbox in Comet browser."""
    try:
        url = "https://mail.google.com/mail/u/0/#inbox"
        webbrowser.open(url)
        return "Gmail inbox opened successfully in Comet browser."
    except ValueError:
        return f"Error: Comet browser not found at {None}"
    except Exception as e:
        return f"Error opening Gmail: {e}"


def open_specific_email(subject: str) -> str:
    """Opens Gmail and searches for a specific email by subject.

    Args:
        subject: The email subject to search for.
    """
    try:
        subject_encoded = quote(subject)
        url = f"https://mail.google.com/mail/u/0/#search/{subject_encoded}"
        webbrowser.open(url)
        return f"Gmail search opened for subject: '{subject}'"
    except ValueError:
        return f"Error: Comet browser not found at {None}"
    except Exception as e:
        return f"Error searching Gmail: {e}"


def compose_email(to: str, subject: str = "", body: str = "") -> str:
    """Opens Gmail compose window with pre-filled fields.

    Args:
        to: Recipient email address.
        subject: Email subject line (optional).
        body: Email body text (optional).
    """
    try:
        to_encoded = quote(to)
        subject_encoded = quote(subject)
        body_encoded = quote(body)
        url = (
            f"https://mail.google.com/mail/?view=cm&fs=1"
            f"&to={to_encoded}&su={subject_encoded}&body={body_encoded}"
        )
        webbrowser.open(url)
        return f"Gmail compose window opened with to='{to}', subject='{subject}'"
    except ValueError:
        return f"Error: Comet browser not found at {None}"
    except Exception as e:
        return f"Error composing email: {e}"
