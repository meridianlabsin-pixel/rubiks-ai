import re
import urllib.request
import urllib.parse
import subprocess
import os


def play_on_youtube(query: str) -> str:
    """Searches YouTube and automatically plays the first video result in Comet browser."""
    try:
        # 1. Search YouTube instantly in the background using Python
        encoded_query = urllib.parse.quote(query)
        req = urllib.request.Request(
            "https://www.youtube.com/results?search_query=" + encoded_query,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        html = urllib.request.urlopen(req).read().decode()
        
        # 2. Extract the very first video ID
        video_ids = re.findall(r"watch\?v=(\S{11})", html)
        
        if video_ids:
            video_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
            
            # 3. Explicitly launch the default browser with the direct video link
            import webbrowser
            webbrowser.open(video_url)
            return f"Playing '{query}' on YouTube."
        else:
            return f"Could not find any YouTube videos for '{query}'."
            
    except Exception as e:
        return f"Failed to play on YouTube: {str(e)}"

def stop_youtube() -> str:
    """Since we open a standard Comet tab, we cannot selectively close it without closing the whole browser."""
    return "Cannot stop standard browser tabs automatically. Please pause or close the tab manually."

if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Iron Man Theme"
    print(play_on_youtube(query))
