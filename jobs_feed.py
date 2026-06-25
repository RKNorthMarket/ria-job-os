import requests
from bs4 import BeautifulSoup
from datetime import datetime

# =========================================================
# RIA ROLE INTELLIGENCE FILTER
# =========================================================

INCLUDE_KEYWORDS = [
    "director",
    "vp",
    "vice president",
    "head",
    "manager",
    "lead",
    "operations",
    "client",
    "service",
    "advisor",
    "wealth",
    "platform",
    "experience"
]

EXCLUDE_KEYWORDS = [
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
# ATS SOURCES (STRUCTURED)
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
# INDEPENDENT RIA CAREER PAGES (CRITICAL ADDITION)
# =========================================================

RIA_CAREERS = [
    {
        "company": "Mercer Advisors",
        "url": "https://www.merceradvisors.com/careers/"
    },
    {
        "company": "Mariner Wealth Advisors",
        "url": "https://www.marinerwealthadvisors.com/careers/"
    },
    {
        "company": "Creative Planning",
        "url": "https://creativeplanning.com/careers/"
    },
    {
        "company": "Wealth Enhancement Group",
        "url": "https://www.wealthenhancement.com/careers"
    }
]

# =========================================================
# HELPERS
# =========================================================

def safe_get_json(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None


def safe_get_html(url):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return None
        return r.text
    except:
        return None

# =========================================================
# GREENHOUSE INGESTION
# =========================================================

def fetch_greenhouse(board):
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
    data = safe_get_json(url)
    if not data:
        return []
    return data.get("jobs", [])


def normalize_greenhouse(job, board):
    return {
        "title": job.get("title", ""),
        "company": job.get("company_name", board),
        "description": job.get("content", ""),
        "link": job.get("absolute_url", ""),
        "source": "greenhouse"
    }

# =========================================================
# LEVER INGESTION
# =========================================================

def fetch_lever(board):
    url = f"https://api.lever.co/v0/postings/{board}?mode=json"
    data = safe_get_json(url)
    return data if isinstance(data, list) else []


def normalize_lever(job, board):
    return {
        "title": job.get("text", ""),
        "company": job.get("company", board),
        "description": job.get("descriptionPlain", ""),
        "link": job.get("hostedUrl", ""),
        "source": "lever"
    }

# =========================================================
# INDEPENDENT RIA SCRAPER (NEW CORE FIX)
# =========================================================

def scrape_ria_careers(company, url):

    html = safe_get_html(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")

    jobs = []

    for a in soup.find_all("a"):

        text = a.get_text(strip=True)
        href = a.get("href")

        if not text or not href:
            continue

        full_text = f"{text} {company}"

        if not is_valid(full_text):
            continue

        jobs.append({
            "title": text,
            "company": company,
            "description": "Direct RIA career page listing",
            "link": href if href.startswith("http") else url,
            "source": "ria_direct"
        })

    return jobs

# =========================================================
# FILTER LOGIC (BALANCED RECALL)
# =========================================================

def is_valid(text):

    t = text.lower()

    if any(b in t for b in EXCLUDE_KEYWORDS):
        return False

    if any(i in t for i in INCLUDE_KEYWORDS):
        return True

    return False

# =========================================================
# MASTER INGESTION ENGINE
# =========================================================

def get_live_jobs():

    jobs = []

    # -------------------------
    # GREENHOUSE
    # -------------------------
    for board in GREENHOUSE_BOARDS:
        raw = fetch_greenhouse(board)

        for j in raw:
            job = normalize_greenhouse(j, board)
            if is_valid(job["title"] + job["description"]):
                jobs.append(job)

    # -------------------------
    # LEVER
    # -------------------------
    for board in LEVER_BOARDS:
        raw = fetch_lever(board)

        for j in raw:
            job = normalize_lever(j, board)
            if is_valid(job["title"] + job["description"]):
                jobs.append(job)

    # -------------------------
    # INDEPENDENT RIA CAREERS
    # -------------------------
    for firm in RIA_CAREERS:
        jobs += scrape_ria_careers(firm["company"], firm["url"])

    # -------------------------
    # DEDUPLICATION
    # -------------------------
    seen = set()
    unique = []

    for j in jobs:
        key = (j["title"], j["company"])

        if key not in seen:
            seen.add(key)
            unique.append(j)

    return unique
