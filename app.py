# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, send_file
import os
import requests
import json
import re
import random
from datetime import datetime, timezone
from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
#  HUGGINGFACE SENTIMENT MODEL (via Inference API)
# ─────────────────────────────────────────────
HF_TOKEN = os.getenv("HF_TOKEN")
SENTIMENT_MODEL = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
API_URL = f"https://api-inference.huggingface.co/models/{SENTIMENT_MODEL}"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def query_hf_api(text: str):
    """Kirim request ke Hugging Face Inference API."""
    try:
        response = requests.post(API_URL, headers=HEADERS, json={"inputs": text}, timeout=10)
        return response.json()
    except Exception as e:
        print(f"API Error: {e}")
        return None

# ─────────────────────────────────────────────
#  LABEL HELPERS
# ─────────────────────────────────────────────
LABEL_SANGAT_NEGATIF = "Sangat Negatif"
LABEL_NEGATIF        = "Negatif"
LABEL_NETRAL         = "Netral"
LABEL_POSITIF        = "Positif"

# Model output → label mapping
# cardiffnlp labels: "negative" | "neutral" | "positive"
MODEL_LABEL_MAP = {
    "negative": ("neg", LABEL_NEGATIF),
    "neutral":  ("netral", LABEL_NETRAL),
    "positive": ("pos", LABEL_POSITIF),
}

app = Flask(__name__)


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def detect_language(text: str) -> str:
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"


def translate_text(text: str, target: str = "en") -> str:
    try:
        result = GoogleTranslator(source="auto", target=target).translate(text[:500])
        return result or text
    except Exception:
        return text


def classify_sentiment(text: str) -> dict:
    """
    Classify sentiment using HuggingFace twitter-xlm-roberta model via API.
    Falls back to keyword-based if API fails.
    """
    api_result = query_hf_api(text[:512])

    # API result is usually a list of lists: [[{'label': '...', 'score': ...}, ...]]
    if not api_result or not isinstance(api_result, list) or "error" in api_result:
        print(f"API result error or empty: {api_result}, fallback to keyword")
        return _fallback_classify(text)

    try:
        # Get the highest score result
        result = api_result[0]
        if isinstance(result, list):
            result = result[0]

        raw_label = result["label"].lower()   # "negative", "neutral", "positive"
        score     = round(result["score"], 4)

        if raw_label == "negative":
            # High confidence → Sangat Negatif
            if score >= 0.85:
                label, level = LABEL_SANGAT_NEGATIF, 3
            else:
                label, level = LABEL_NEGATIF, 2
        elif raw_label == "neutral":
            label, level = LABEL_NETRAL, 1
        else:  # positive
            label, level = LABEL_POSITIF, 0

        return {
            "label":        label,
            "level":        level,
            "score":        score,
            "neg_keywords": [],
            "pos_keywords": [],
            "neg_count":    0,
            "model":        "xlm-roberta-api",
        }

    except (KeyError, IndexError) as e:
        print(f"Model parsing error: {e}, fallback to keyword")
        return _fallback_classify(text)


# ── Fallback keyword-based (jika model gagal dimuat) ──────
_NEGATIVE_KW = [
    "benci","bodoh","tolol","idiot","sampah","bangsat","anjing","goblok",
    "kampret","brengsek","bajingan","laknat","kurang ajar","mati","bunuh",
    "setan","iblis","jahat","bohong","manipulasi","fitnah","sesat","hina",
    "jijik","mual","muntah","muak","najis","busuk","kotor","babi","tai",
    "dungu","bebal","penipu","pecundang","caci","maki","kafir","pendosa",
    "hate","stupid","idiot","trash","garbage","loser","die","kill","moron",
    "dumb","ugly","disgusting","pathetic","liar","manipulate","fraud","evil",
    "wicked","jerk","worthless","annoying","cringe","fake","clown","brainless",
    "toxic","bully","harass","abuse","stfu","kys","gtfo","ratio",
]
_POSITIVE_KW = [
    "bagus","keren","mantap","suka","love","great","nice","good","amazing",
    "awesome","salut","respect","proud","bangga","hebat","luar biasa","support",
    "dukung","setuju","brilliant","happy","baik",
]

def _fallback_classify(text: str) -> dict:
    t = text.lower()
    neg_hits = [kw for kw in _NEGATIVE_KW if kw in t]
    pos_hits = [kw for kw in _POSITIVE_KW if kw in t]
    neg_count = len(neg_hits)
    pos_count = len(pos_hits)

    if neg_count >= 3:
        label, level = LABEL_SANGAT_NEGATIF, 3
    elif neg_count >= 1:
        label, level = LABEL_NEGATIF, 2
    elif pos_count >= 1:
        label, level = LABEL_POSITIF, 0
    else:
        label, level = LABEL_NETRAL, 1

    return {
        "label":        label,
        "level":        level,
        "score":        None,
        "neg_keywords": neg_hits[:5],
        "pos_keywords": pos_hits[:3],
        "neg_count":    neg_count,
        "model":        "keyword-fallback",
    }


# ─────────────────────────────────────────────
#  TWITTER SCRAPING via auth_token
# ─────────────────────────────────────────────

def get_csrf_token(auth_token: str) -> str:
    try:
        session = requests.Session()
        session.cookies.set("auth_token", auth_token, domain=".twitter.com")
        session.get(
            "https://twitter.com/i/api/2/badge_count/badge_count.json",
            headers={
                "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LTMQLSrdih0K0j6TSADAOkOzqytqPexPjEsxHfCTZO",
                "x-twitter-active-user": "yes",
                "x-twitter-auth-type": "OAuth2Session",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            },
            timeout=10,
        )
        ct0 = session.cookies.get("ct0") or ""
        if ct0:
            return ct0
    except Exception:
        pass
    import secrets
    return secrets.token_hex(32)


def build_headers(auth_token: str, csrf_token: str) -> dict:
    return {
        "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LTMQLSrdih0K0j6TSADAOkOzqytqPexPjEsxHfCTZO",
        "cookie": f"auth_token={auth_token}; ct0={csrf_token}",
        "x-csrf-token": csrf_token,
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "x-twitter-auth-type": "OAuth2Session",
        "x-twitter-client-language": "en",
        "x-twitter-active-user": "yes",
        "referer": "https://twitter.com/",
    }


def search_tweets(query: str, auth_token: str, max_results: int = 20, ct0: str = "") -> list:
    csrf = ct0 if ct0 else get_csrf_token(auth_token)
    headers = build_headers(auth_token, csrf)

    variables = {
        "rawQuery": query,
        "count": max_results,
        "querySource": "typed_query",
        "product": "Latest",
    }
    features = {
        "rweb_lists_timeline_redesign_enabled": True,
        "responsive_web_graphql_exclude_directive_enabled": True,
        "verified_phone_label_enabled": False,
        "creator_subscriptions_tweet_preview_api_enabled": True,
        "responsive_web_graphql_timeline_navigation_enabled": True,
        "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
        "tweetypie_unmention_optimization_enabled": True,
        "responsive_web_edit_tweet_api_enabled": True,
        "graphql_is_translatable_rweb_tweet_and_user_result_enabled": True,
        "view_counts_everywhere_api_enabled": True,
        "longform_notetweets_consumption_enabled": True,
        "tweet_awards_web_tipping_enabled": False,
        "freedom_of_speech_not_reach_decide_filtered_timeline_enabled": True,
        "standardized_nudges_misinfo": True,
        "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
        "longform_notetweets_rich_text_read_enabled": True,
        "longform_notetweets_inline_media_enabled": True,
        "responsive_web_enhance_cards_enabled": False,
    }

    params = {
        "variables": json.dumps(variables),
        "features":  json.dumps(features),
    }
    url = "https://twitter.com/i/api/graphql/nK1dw4oV3k4w5TdtcAdSww/SearchTimeline"

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        return _parse_tweets(resp.json())
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code if getattr(e, 'response', None) is not None else 0
        if code in [401, 403, 400]:
            print(f"Auth token block (Code {code}). Menggunakan Fallback Scraper Nitter...")
            return _fallback_scrape(query, max_results)
        elif code == 429:
            raise ValueError("Rate limit Twitter. Coba lagi beberapa menit kemudian.")
        raise ValueError(f"HTTP Error {code}: {str(e)}")
    except requests.exceptions.Timeout:
        raise ValueError("Request timeout. Periksa koneksi internet Anda.")
    except Exception as e:
        raise ValueError(f"Gagal mengambil data: {str(e)}")

import urllib.parse
from bs4 import BeautifulSoup
import json

def _fallback_scrape(query: str, max_results: int) -> list:
    """Fallback scraping ke Twitter Syndication API (tanpa auth_token).
    Catatan: Syndication biasa berbasis profile/user. Jika query berupa keyword, 
    kita ambil keyword pertama sbg 'user' asumsi. Ini adalah best-effort fallback.
    """
    # Ambil kata pertama tanpa hashtag/simbol sebagai target profile
    clean_query = ''.join(e for e in query.split()[0] if e.isalnum())
    if not clean_query:
        clean_query = "twitter"
        
    url = f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{clean_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        
        # Syndication mengembalikan HTML dengan tag <script id="__NEXT_DATA__"> berisi JSON data
        soup = BeautifulSoup(resp.text, 'html.parser')
        script_tag = soup.find('script', id='__NEXT_DATA__')
        
        if not script_tag:
            raise ValueError("Struktur data Syndication berubah.")
            
        data = json.loads(script_tag.string)
        instructions = (
            data.get("props", {})
            .get("pageProps", {})
            .get("timeline", {})
            .get("entries", [])
        )
        
        tweets = []
        for entry in instructions:
            if len(tweets) >= max_results:
                break
                
            if entry.get("type") != "tweet":
                continue
                
            tweet_data = entry.get("content", {}).get("tweet", {})
            if not tweet_data:
                continue
                
            text = tweet_data.get("text", "")
            if not text:
                continue
                
            user_data = tweet_data.get("user", {})
            
            tw = {
                "id": tweet_data.get("id_str", str(hash(text))),
                "text": text,
                "created_at": tweet_data.get("created_at", ""),
                "retweet_count": tweet_data.get("retweet_count", 0),
                "like_count": tweet_data.get("favorite_count", 0),
                "reply_count": tweet_data.get("reply_count", 0),
                "quote_count": tweet_data.get("quote_count", 0),
                "user": {
                    "name": user_data.get("name", "Unknown"),
                    "screen_name": user_data.get("screen_name", "unknown"),
                    "followers": user_data.get("followers_count", 0),
                    "profile_image": user_data.get("profile_image_url_https", ""),
                },
            }
            tweets.append(tw)
            
        return tweets
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code if getattr(e, 'response', None) is not None else 0
        if code == 404:
             return [] # User/Topik tidak ditemukan
        print(f"Fallback Syndication HTTP Error: {e}")
        raise ValueError(f"Gagal memuat fallback (API Utama 401 & Syndication {code}). Pastikan auth_token valid.")
    except Exception as e:
        print(f"Fallback Syndication Error: {e}")
        raise ValueError(f"Gagal mengambil data dari API Utama & Scraper Cadangan. ({e})")


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


def _extract_tweet(result: dict) -> dict | None:
    try:
        if result.get("__typename") == "TweetWithVisibilityResults":
            result = result.get("tweet", {})
        legacy = result.get("legacy", {})
        user_legacy = (
            result.get("core", {})
            .get("user_results", {})
            .get("result", {})
            .get("legacy", {})
        )
        text = legacy.get("full_text", "") or legacy.get("text", "")
        if not text:
            return None
        return {
            "id": legacy.get("id_str", ""),
            "text": text,
            "created_at": legacy.get("created_at", ""),
            "retweet_count":  legacy.get("retweet_count", 0),
            "like_count":     legacy.get("favorite_count", 0),
            "reply_count":    legacy.get("reply_count", 0),
            "quote_count":    legacy.get("quote_count", 0),
            "user": {
                "name":          user_legacy.get("name", "Unknown"),
                "screen_name":   user_legacy.get("screen_name", "unknown"),
                "followers":     user_legacy.get("followers_count", 0),
                "profile_image": user_legacy.get("profile_image_url_https", ""),
            },
        }
    except Exception:
        return None


# ─────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return send_file(os.path.join(os.path.dirname(__file__), "index.html"))

# ── Endpoints auto-token / Playwright dihilangkan karena aplikasi berjalan di Web ──

@app.route("/analyze", methods=["POST"])
def analyze():
    data         = request.get_json()
    query        = (data.get("query") or "").strip()
    auth_token   = (data.get("auth_token") or "").strip()
    ct0          = (data.get("ct0") or "").strip()
    max_results  = min(int(data.get("max_results", 20)), 50)
    translate_to = data.get("translate_to", "id")

    if not query:
        return jsonify({"error": "Query tidak boleh kosong."}), 400
    if not auth_token:
        return jsonify({"error": "Auth token tidak boleh kosong."}), 400

    try:
        raw_tweets = search_tweets(query, auth_token, max_results, ct0=ct0)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if not raw_tweets:
        return jsonify({
            "error": "Tidak ada tweet ditemukan. Pastikan query benar dan auth_token valid.",
        }), 200

    results = []
    for tw in raw_tweets:
        text = tw["text"]
        lang = detect_language(text)

        # Translate if language differs from target
        translated = None
        if lang != translate_to and lang != "unknown":
            translated = translate_text(text, target=translate_to)

        sentiment = classify_sentiment(text)

        results.append({
            "id":           tw["id"],
            "text":         text,
            "translated":   translated,
            "lang":         lang,
            "translate_to": translate_to,
            "sentiment":    sentiment,
            "metrics": {
                "retweet_count": tw["retweet_count"],
                "like_count":    tw["like_count"],
                "reply_count":   tw["reply_count"],
                "quote_count":   tw["quote_count"],
            },
            "user": tw["user"],
        })

    total          = len(results)
    very_neg_count = sum(1 for r in results if r["sentiment"]["level"] == 3)
    neg_count      = sum(1 for r in results if r["sentiment"]["level"] >= 2)
    netral_count   = sum(1 for r in results if r["sentiment"]["level"] == 1)
    positif_count  = sum(1 for r in results if r["sentiment"]["level"] == 0)

    summary = {
        "total":          total,
        "very_neg_count": very_neg_count,
        "neg_count":      neg_count,
        "netral_count":   netral_count,
        "positif_count":  positif_count,
        "neg_pct":        round(neg_count / total * 100, 1) if total else 0,
        "very_neg_pct":   round(very_neg_count / total * 100, 1) if total else 0,
    }

    return jsonify({"tweets": results, "summary": summary})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
