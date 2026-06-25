from datetime import datetime
import requests

# =========================================================
# ATS ONLY (NO DISCOVERY HERE ANYMORE)
# =========================================================

def safe_get(url, mode="text"):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        return r.json() if mode == "json" else r.text
    except:
        return None

# =========================================================
# GREENHOUSE ONLY
# =========================================================

def fetch_greenhouse(board):
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
    data = safe_get(url, "json")
    return data.get("jobs", []) if data else []

def normalize_greenhouse(job, board):

    return {
        "title": job.get("title", ""),
        "company": board,
        "link": job.get("absolute_url", ""),
        "source": "greenhouse",
        "date": datetime.now().strftime("%Y-%m-%d")
    }

# =========================================================
# LEVER ONLY
# =========================================================

def fetch_lever(board):
    url = f"https://api.lever.co/v0/postings/{board}?mode=json"
    data = safe_get(url, "json")
    return data if isinstance(data, list) else []

def normalize_lever(job, board):

    return {
        "title": job.get("text", ""),
        "company": board,
        "link": job.get("hostedUrl", ""),
        "source": "lever",
        "date": datetime.now().strftime("%Y-%m-%d")
    }

# =========================================================
# MASTER ATS FALLBACK
# =========================================================

def get_ats_jobs():

    return []  # intentionally minimal now
