import re
from web_tools import search_web

def get_weather(location: str) -> str:
    """
    Fetches the current weather for a specified location using Open-Meteo (free, no API key needed).
    Falls back to web search if the API fails.
    """
    try:
        import urllib.request
        import json

        # Step 1: Geocode the location name to lat/lon using Open-Meteo's geocoding API
        encoded_loc = urllib.parse.quote(location)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_loc}&count=1&language=en&format=json"
        geo_req = urllib.request.urlopen(geo_url, timeout=8)
        geo_data = json.loads(geo_req.read())

        results = geo_data.get("results", [])
        if not results:
            # Fallback to web search
            return _weather_fallback(location)

        lat = results[0]["latitude"]
        lon = results[0]["longitude"]
        city_name = results[0].get("name", location)
        country = results[0].get("country", "")

        # Step 2: Get actual weather data from Open-Meteo
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current_weather=true"
            f"&hourly=relative_humidity_2m"
            f"&timezone=auto"
        )
        w_req = urllib.request.urlopen(weather_url, timeout=8)
        w_data = json.loads(w_req.read())

        current = w_data.get("current_weather", {})
        temp = current.get("temperature", "N/A")
        windspeed = current.get("windspeed", "N/A")
        weathercode = current.get("weathercode", -1)

        # Decode weather code to human-readable condition
        condition = _decode_weather_code(weathercode)

        # Get humidity from hourly data (first entry = current hour)
        humidity = "N/A"
        hourly = w_data.get("hourly", {})
        humidity_list = hourly.get("relative_humidity_2m", [])
        if humidity_list:
            humidity = f"{humidity_list[0]}%"

        return (
            f"Weather in {city_name}, {country}:\n"
            f"🌡️ Temperature: {temp}°C\n"
            f"🌤️ Condition: {condition}\n"
            f"💨 Wind: {windspeed} km/h\n"
            f"💧 Humidity: {humidity}"
        )

    except Exception as e:
        return _weather_fallback(location)


def _weather_fallback(location: str) -> str:
    """Fallback: use DuckDuckGo web search for weather info."""
    try:
        result = search_web(f"weather in {location} today temperature")
        if result and "No results" not in result:
            return f"Weather info for {location} (from web):\n{result}"
        return f"Couldn't fetch weather for {location}. Web search also returned no results."
    except Exception:
        return f"Couldn't fetch weather for {location}. All methods failed."


def _decode_weather_code(code: int) -> str:
    """Converts WMO weather interpretation code to a human-readable string."""
    codes = {
        0: "Clear sky ☀️",
        1: "Mainly clear 🌤️",
        2: "Partly cloudy ⛅",
        3: "Overcast ☁️",
        45: "Foggy 🌫️",
        48: "Depositing rime fog 🌫️",
        51: "Light drizzle 🌦️",
        53: "Moderate drizzle 🌦️",
        55: "Dense drizzle 🌧️",
        61: "Slight rain 🌧️",
        63: "Moderate rain 🌧️",
        65: "Heavy rain 🌧️",
        71: "Slight snowfall 🌨️",
        73: "Moderate snowfall 🌨️",
        75: "Heavy snowfall ❄️",
        80: "Slight rain showers 🌦️",
        81: "Moderate rain showers 🌧️",
        82: "Violent rain showers ⛈️",
        95: "Thunderstorm ⛈️",
        96: "Thunderstorm with slight hail ⛈️",
        99: "Thunderstorm with heavy hail ⛈️",
    }
    return codes.get(code, "Unknown")


import urllib.parse
