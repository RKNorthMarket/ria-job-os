import requests
from datetime import datetime

# =========================================================
# DIRECT ATS ENTRY POINTS (NO SEARCH ENGINES)
# =========================================================

GREENHOUSE_BOARDS = [
    "hightoweradvisors",
    "focusfinancialpartners",
    "commonwealthfinancialnetwork"
]

LEVER_BOARDS = [
    "focusfinancialpartners",
    "marinerwealthadvisors"
]

# =========================================================
# SAFE GET
# =========================================================

def safe_get(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# =========================================================
# GREENHOUSE FETCH
# =========================================================

def fetch_greenhouse(board):

    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
    data = safe_get(url)

    return data.get("jobs", []) if data else []

# =========================================================
# LEVER FETCH
# =========================================================

def fetch_lever(board):

    url = f"https://api.lever.co/v0/postings/{board}?mode=json"
    data = safe_get(url)

    return data if isinstance(data, list) else []

# =========================================================
# SURFACE JOB ENGINE (STABLE)
# =========================================================

def get_surface_jobs():

    jobs = []

    # Greenhouse
    for b in GREENHOUSE_BOARDS:
        for j in fetch_greenhouse(b):
            jobs.append({
                "title": j.get("title"),
                "company": b,
                "link": j.get("absolute_url"),
                "source": "greenhouse",
                "date": datetime.now().strftime("%Y-%m-%d")
            })

    # Lever
    for b in LEVER_BOARDS:
        for j in fetch_lever(b):
            jobs.append({
                "title": j.get("text"),
                "company": b,
                "link": j.get("hostedUrl"),
                "source": "lever",
                "date": datetime.now().strftime("%Y-%m-%d")
            })

    return jobs
