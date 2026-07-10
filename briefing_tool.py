import urllib.request
import json

def get_morning_briefing() -> str:
    """Fetches a morning briefing including weather, top news, and system status."""
    briefing = "Good morning, Boss. Here is your daily briefing:\n\n"
    
    # System Status
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.5)
        batt = psutil.sensors_battery()
        batt_str = f"{batt.percent}%" if batt else "Plugged in / Desktop"
        briefing += f"SYSTEM STATUS:\n- CPU Usage: {cpu}%\n- Battery: {batt_str}\n\n"
    except ImportError:
        briefing += "SYSTEM STATUS:\n- psutil not installed. Cannot fetch CPU/Battery stats.\n\n"
    
    # Weather (Using Open-Meteo for IP-based approximate location weather)
    try:
        # Get IP location
        ip_req = urllib.request.urlopen("http://ip-api.com/json")
        loc_data = json.loads(ip_req.read())
        lat, lon = loc_data.get("lat"), loc_data.get("lon")
        city = loc_data.get("city", "your location")
        
        # Get Weather
        if lat and lon:
            weather_req = urllib.request.urlopen(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true")
            w_data = json.loads(weather_req.read())
            current = w_data.get("current_weather", {})
            temp = current.get("temperature", "Unknown")
            briefing += f"WEATHER in {city}:\n- Temperature: {temp}°C\n\n"
    except Exception as e:
        briefing += f"WEATHER:\n- Failed to fetch weather data.\n\n"
        
    # Top News (Using simple RSS or duckduckgo html parsing)
    # To keep dependencies light, we will just use a reliable free API or scrape.
    # The NewsData API is good but requires a key. Let's use a public RSS feed feedparser or just regex.
    try:
        import re
        html = urllib.request.urlopen("https://news.ycombinator.com/").read().decode('utf-8')
        titles = re.findall(r'<span class="titleline"><a href="[^"]+">([^<]+)</a>', html)
        briefing += "TOP TECH NEWS:\n"
        for i, title in enumerate(titles[:3]):
            briefing += f"- {title}\n"
    except Exception:
        briefing += "TOP NEWS:\n- Failed to fetch news.\n"
        
    return briefing
