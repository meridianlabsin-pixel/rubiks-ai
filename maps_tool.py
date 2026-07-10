import webbrowser
"""
Google Maps tool for RUBIKS AI assistant.
Opens directions and location searches in Comet browser via Google Maps.
"""

import subprocess
from urllib.parse import quote



def get_directions(destination: str, origin: str = "") -> str:
    """Opens Google Maps directions from origin to destination in Comet browser.

    Args:
        destination: The destination address or place name.
        origin: The starting address or place name. If empty, uses current location (Google Maps auto-detects).

    Returns:
        A string confirming the directions were opened or describing the error.
    """
    try:
        origin_part = quote(origin, safe="+") if origin else "My+Location"
        destination_part = quote(destination, safe="+")
        url = f"https://www.google.com/maps/dir/{origin_part}/{destination_part}"
        webbrowser.open(url)
        origin_display = origin if origin else "your current location"
        return f"Opened directions from {origin_display} to {destination} in Comet browser."
    except Exception as e:
        return f"Error opening directions: {e}"


def show_on_map(location: str) -> str:
    """Opens a location on Google Maps in Comet browser.

    Args:
        location: The place name, address, or coordinates to search for on Google Maps.

    Returns:
        A string confirming the map was opened or describing the error.
    """
    try:
        location_encoded = quote(location, safe="+")
        url = f"https://www.google.com/maps/search/{location_encoded}"
        webbrowser.open(url)
        return f"Opened {location} on Google Maps in Comet browser."
    except Exception as e:
        return f"Error opening map: {e}"
