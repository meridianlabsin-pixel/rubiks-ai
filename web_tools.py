import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

def search_web(query: str) -> str:
    """Searches the web securely and instantly using DuckDuckGo Lite HTML."""
    try:
        # We bypass the massive headless browser for raw searches because 
        # search engines heavily block Playwright with Captchas/Bot challenges.
        # This raw POST request to DDG's legacy Lite server bypasses the firewall.
        data = urllib.parse.urlencode({'q': query}).encode('utf-8')
        req = urllib.request.Request(
            'https://lite.duckduckgo.com/lite/', 
            data=data, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        
        results = []
        # DDG Lite uses tables. The actual result link and title is in td.result-snippet or similar.
        # We can extract all elements with class 'result-snippet'
        snippets = soup.find_all('td', class_='result-snippet')
        links = soup.find_all('a', class_='result-url')
        
        for i in range(min(3, len(snippets))):
            snippet_text = snippets[i].text.strip()
            link_url = links[i]['href'] if i < len(links) else "No link"
            
            # The title is usually in the previous row, but extracting snippet + url is enough for the LLM
            results.append(f"Info: {snippet_text}\nLink: {link_url}")
            
        if not results:
            return f"No results found on the web for '{query}'."
            
        return "\n\n".join(results)
    except Exception as e:
        return f"Web search failed: {str(e)}"
