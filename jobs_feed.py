import requests
from datetime import datetime

# =========================================================
# RIA ROLE FILTER (STRICT)
# =========================================================

ALLOWED_KEYWORDS = [
    "director",
    "vp",
    "vice president",
    "head",
    "operations",
    "client service",
    "wealth",
    "ria",
    "advisor"
]

BLOCKED_KEYWORDS = [
    "engineer",
    "software",
    "developer",
    "it",
    "marketing",
    "accountant",
    "payroll",
    "teacher",
    "chef",
    "mortgage"
]

# =========================================================
# SOURCES (SAFE + COMMON ATS)
# =========================================================

GREENHOUSE_BOARDS = [
    "hightoweradvisors",
    "commonwealthfinancialnetwork",
    "focusfinancialpartners"
]

LEVER_BOARDS = [
    "assetmark",
    "lplfinancial",
    "cetera"
]

# =========================================================
# FETCH HELPERS
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
# GREENHOUSE
# =========================================================

def fetch_greenhouse(board):
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
    data = safe_get(url)
    if not data:
        return []
    return data.get("jobs", [])

# =========================================================
# LEVER
# =========================================================

def fetch_lever(board):
    url = f"https://api.lever.co/v0/postings/{board}?mode=json"
    data = safe_get(url)
    return data if isinstance(data, list) else []

# =========================================================
# FILTER LOGIC
# =========================================================

def is_valid_job(text):

    text = text.lower()

    if any(b in text for b in BLOCKED_KEYWORDS):
        return False

    if any(a in text for a in ALLOWED_KEYWORDS):
        return True

    return False

# =========================================================
# NORMALIZATION
# =========================================================

def normalize_job(title, company, link, description):

    text = f"{title} {description}"

    if not is_valid_job(text):
        return None

    return {
        "title": title,
        "company": company,
        "link": link,
        "description": description,
        "source": "live",
        "date": datetime.now().strftime("%Y-%m-%d")
    }

# =========================================================
# INGESTION ENGINE
# =========================================================

def get_live_jobs():

    jobs = []

    # GREENHOUSE
    for board in GREENHOUSE_BOARDS:
        raw = fetch_greenhouse(board)

        for j in raw:
            job = normalize_job(
                j.get("title", ""),
                j.get("company_name", board),
                j.get("absolute_url", ""),
                j.get("content", "")
            )
            if job:
                jobs.append(job)

    # LEVER
    for board in LEVER_BOARDS:
        raw = fetch_lever(board)

        for j in raw:
            job = normalize_job(
                j.get("text", ""),
                j.get("company", board),
                j.get("hostedUrl", ""),
                j.get("descriptionPlain", "")
            )
            if job:
                jobs.append(job)

    # DEDUPE
    seen = set()
    unique = []

    for j in jobs:
        key = (j["title"], j["company"])
        if key not in seen:
            seen.add(key)
            unique.append(j)

    return unique
