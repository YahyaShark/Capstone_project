import urllib.parse
import json
from playwright.sync_api import sync_playwright

def inspect_json():
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True, channel="msedge")
        except:
            browser = p.chromium.launch(headless=True)
            
        context = browser.new_context()
        page = context.new_page()
        
        found = []
        
        def handle_response(response):
            if "SearchTimeline" in response.url and response.status == 200:
                try:
                    data = response.json()
                    instructions = (
                        data.get("data", {})
                        .get("search_by_raw_query", {})
                        .get("search_timeline", {})
                        .get("timeline", {})
                        .get("instructions", [])
                    )
                    for instr in instructions:
                        for entry in instr.get("entries", []):
                            result = (
                                entry.get("content", {})
                                .get("itemContent", {})
                                .get("tweet_results", {})
                                .get("result", {})
                            )
                            if result and len(found) < 2:
                                found.append(result)
                except Exception as e:
                    print("Error parsing", e)
                    
        page.on("response", handle_response)
        
        try:
            page.goto("https://x.com/search?q=polisi&src=typed_query", timeout=20000)
            page.wait_for_timeout(8000)
        except Exception:
            pass
            
        browser.close()
        
        with open("debug_tweet.json", "w", encoding="utf-8") as f:
            json.dump(found, f, indent=2)

if __name__ == "__main__":
    inspect_json()
