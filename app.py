# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, send_file
import os
import requests
import json
import re
import random
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
#  HUGGINGFACE SENTIMENT MODEL (via Inference API)
# ─────────────────────────────────────────────
HF_TOKEN = os.getenv("HF_TOKEN")
SENTIMENT_MODEL = "w11wo/indonesian-roberta-base-sentiment-classifier"
API_URL = f"https://router.huggingface.co/hf-inference/models/{SENTIMENT_MODEL}"
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
# Fitur terjemahan dan deteksi bahasa dihapus untuk fokus pada Bahasa Indonesia.



def classify_sentiment(text: str) -> dict:
    """
    Classify sentiment using HuggingFace RoBERTa model via API (Full-Sentence Context).
    """
    api_result = query_hf_api(text[:512])

    if not api_result or not isinstance(api_result, list) or "error" in api_result:
        # Jika API server down/gagal, kembalikan label Netral, jangan fallback mencari per kata.
        print(f"API result error or empty: {api_result}")
        return {
            "label":        LABEL_NETRAL,
            "level":        1,
            "score":        0.0,
            "neg_keywords": [],
            "pos_keywords": [],
            "neg_count":    0,
            "model":        "API_DOWN_LOCKED",
        }

    try:
        result = api_result[0]
        if isinstance(result, list):
            result = result[0]

        raw_label = result["label"].lower()
        score     = round(result["score"], 4)

        if raw_label == "negative":
            # KALIBRASI SENSITIVITAS (RE-TRAINING THRESHOLD)
            # Mengatasi bug model over-sensitive: jika dia merasa negatif tapi ragu (score di bawah 0.75), paksa menjadi Netral
            if score < 0.75:
                label, level = LABEL_NETRAL, 1
            elif score >= 0.95:
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
        print(f"Model parsing error: {e}")
        return {
            "label":        LABEL_NETRAL,
            "level":        1,
            "score":        0.0,
            "neg_keywords": [],
            "pos_keywords": [],
            "neg_count":    0,
            "model":        "API_PARSE_ERROR",
        }


# ─────────────────────────────────────────────
#  TWITTER SCRAPING via auth_token
# ─────────────────────────────────────────────

def search_tweets(query: str, auth_token: str, max_results: int = 20) -> list:
    import subprocess
    import json
    import os
    
    script_path = os.path.join(os.path.dirname(__file__), "scraper.py")
    res = subprocess.run(
        ["python", script_path, query, auth_token, str(max_results)],
        capture_output=True, text=True, timeout=90
    )
    
    try:
        out = json.loads(res.stdout)
        if out.get("success"):
            tweets = out.get("data", [])
            return tweets
        else:
            raise ValueError(f"{out.get('error')}")
    except json.JSONDecodeError:
        raise ValueError(f"Sistem Gagal. Engine diblokir X.com atau timeout. Error logic: {res.stderr}")


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
    auth_token   = (data.get("auth_token") or "").strip().strip('"').strip("'")
    max_results  = min(int(data.get("max_results", 20)), 50)

    if not query:
        return jsonify({"error": "Query tidak boleh kosong."}), 400
    if not auth_token:
        return jsonify({"error": "Auth token tidak boleh kosong."}), 400

    try:
        raw_tweets = search_tweets(query, auth_token, max_results)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if not raw_tweets:
        return jsonify({
            "error": "Tidak ada tweet ditemukan. Pastikan query benar dan auth_token valid.",
        }), 200

    results = []
    for tw in raw_tweets:
        text = tw["text"]

        sentiment = classify_sentiment(text)

        results.append({
            "id":           tw["id"],
            "text":         text,
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
