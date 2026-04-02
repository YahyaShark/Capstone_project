import sys
import json
import urllib.parse
from playwright.sync_api import sync_playwright

def _find_key(obj, key):
    if isinstance(obj, dict):
        if key in obj: return obj[key]
        for v in obj.values():
            res = _find_key(v, key)
            if res is not None: return res
    elif isinstance(obj, list):
        for item in obj:
            res = _find_key(item, key)
            if res is not None: return res
    return None

def _extract_tweet(result: dict) -> dict:
    try:
        if result.get("__typename") == "TweetWithVisibilityResults":
            result = result.get("tweet", {})
            
        legacy = result.get("legacy") or _find_key(result, "legacy") or {}
        
        # Mengekstrak nama, screen_name, foto via rekursif karena X sengaja mengacak nesting 'core' dan 'user_results'
        name = _find_key(result, "name") or "Unknown"
        screen_name = _find_key(result, "screen_name") or "unknown"
        followers = _find_key(result, "followers_count") or 0
        profile_image = _find_key(result, "profile_image_url_https") or ""
        
        text = _find_key(result, "full_text") or _find_key(result, "text") or ""
        
        if not text:
            return None
            
        return {
            "id": _find_key(result, "id_str") or "",
            "text": text,
            "created_at": _find_key(result, "created_at") or "",
            "retweet_count":  _find_key(result, "retweet_count") or 0,
            "like_count":     _find_key(result, "favorite_count") or 0,
            "reply_count":    _find_key(result, "reply_count") or 0,
            "quote_count":    _find_key(result, "quote_count") or 0,
            "user": {
                "name":          name,
                "screen_name":   screen_name,
                "followers":     followers,
                "profile_image": profile_image,
            },
        }
    except Exception:
        return None

def _parse_tweets(data: dict) -> list:
    tweets = []
    try:
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
                if not result:
                    continue
                tw = _extract_tweet(result)
                if tw:
                    tweets.append(tw)
    except Exception:
        pass
    return tweets


def run_scraper(query, auth_token, max_results):
    tweets_dict = {}
    
    with sync_playwright() as p:
        # Gunakan channel=msedge atau chrome agar tidak memicu Windows Firewall untuk nodejs/chromium
        # jika gagal pakai channel="msedge", fallback ke chromium bawaan
        try:
            browser = p.chromium.launch(headless=True, channel="msedge")
        except:
            browser = p.chromium.launch(headless=True)
            
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        # Auth Token
        context.add_cookies([{
            "name": "auth_token",
            "value": auth_token,
            "domain": ".x.com",
            "path": "/"
        }])
        
        page = context.new_page()
        
        def handle_response(response):
            if "SearchTimeline" in response.url and response.status == 200:
                try:
                    data = response.json()
                    parsed = _parse_tweets(data)
                    for tw in parsed:
                        tweets_dict[tw["id"]] = tw
                except Exception:
                    pass
                    
        page.on("response", handle_response)
        
        encoded_query = urllib.parse.quote(query)
        try:
            page.goto(f"https://x.com/search?q={encoded_query}&src=typed_query", timeout=30000)
            
            try:
                page.wait_for_selector('[data-testid="tweet"]', timeout=15000)
            except Exception:
                pass
            
            retries = 0
            while len(tweets_dict) < max_results and retries < 5:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)
                retries += 1
                
        except Exception as e:
            pass
            
        browser.close()
        
    results = list(tweets_dict.values())
    return results[:max_results]

if __name__ == "__main__":
    query = sys.argv[1]
    auth_token = sys.argv[2]
    max_results = int(sys.argv[3])
    
    try:
        data = run_scraper(query, auth_token, max_results)
        if not data:
            print(json.dumps({"success": False, "error": "Token salah, atau tidak ada tweet yang didapatkan dari topik ini (Playwright gagal menarik respons)."}))
        else:
            print(json.dumps({"success": True, "data": data}))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
