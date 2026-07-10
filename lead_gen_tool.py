from playwright.sync_api import sync_playwright
import urllib.parse
import time

def find_leads(query: str, location: str) -> str:
    """
    Scrapes Google Maps for business leads (companies, stores, offices).
    Use this when the user asks to find leads, companies, or places in a specific location.
    """
    search_term = urllib.parse.quote(f"{query} in {location}")
    url = f"https://www.google.com/maps/search/{search_term}"
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Navigate and wait for results to load
            page.goto(url)
            page.wait_for_selector('a[href*="/maps/place/"]', timeout=15000)
            
            # Scroll to load a few leads
            page.mouse.wheel(0, 1000)
            time.sleep(2)
            
            # Extract lead data
            leads = []
            elements = page.query_selector_all('a[href*="/maps/place/"]')
            
            for el in elements:
                name = el.get_attribute('aria-label')
                if name and name not in leads:
                    leads.append(name)
                    if len(leads) >= 10:
                        break
                        
            browser.close()
            
            if not leads:
                return f"No leads found for '{query}' in '{location}'."
                
            formatted = f"Leads Found for '{query}' in '{location}':\n"
            for i, l in enumerate(leads):
                formatted += f"{i+1}. {l}\n"
                
            return formatted
    except Exception as e:
        return f"Lead generation failed: {str(e)}"
