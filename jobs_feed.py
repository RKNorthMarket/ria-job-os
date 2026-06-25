import requests
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# =========================================================
# RIA UNIVERSE (STABLE SEED)
# =========================================================

RIA_FIRMS = [
    "Focus Financial Partners",
    "Hightower Advisors",
    "Commonwealth Financial Network",
    "LPL Financial",
    "Ameriprise Financial",
    "Raymond James",
    "Cetera Financial",
    "AssetMark",
    "Mercer Advisors",
    "Mariner Wealth Advisors",
    "Creative Planning",
    "Wealth Enhancement Group",
    "Carson Group",
    "Captrust",
    "Baird Private Wealth"
]

# =========================================================
# SAFE REQUEST
# =========================================================

def safe_get(url, mode="text"):
    try:
        r = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        if r.status_code != 200:
            return None
        return r.json() if mode == "json" else r.text
    except:
        return None

# =========================================================
# JOB SIGNALS (BALANCED FILTER)
# =========================================================

JOB_KEYWORDS = [
    "director", "vp", "vice president", "head",
    "manager", "lead", "operations", "client",
    "advisor", "wealth", "service", "associate",
    "specialist", "analyst", "relationship"
]

NOISE_KEYWORDS = [
    "contact", "privacy", "terms", "cookie",
    "life at", "culture", "about", "blog",
    "news", "press", "events", "insights"
]

def is_valid_job_text(text: str) -> bool:
    t = text.lower()

    if len(text) < 6:
        return False

    if any(n in t for n in NOISE_KEYWORDS):
        return False

    return any(k in t for k in JOB_KEYWORDS)

# =========================================================
# ATS LAYER (SAFE)
# =========================================================

def fetch_greenhouse(board):
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
    data = safe_get(url, "json")
    return data.get("jobs", []) if data else []

def normalize_greenhouse(job, board):
    title = job.get("title")
    url = job.get("absolute_url")

    if not title or not url:
        return None

    if not is_valid_job_text(title):
        return None

    return {
        "title": title,
        "company": board,
        "description": "Greenhouse ATS job",
        "link": url,
        "source": "greenhouse",
        "date": datetime.now().strftime("%Y-%m-%d")
    }

def fetch_lever(board):
    url = f"https://api.lever.co/v0/postings/{board}?mode=json"
    data = safe_get(url, "json")
    return data if isinstance(data, list) else []

def normalize_lever(job, board):
    title = job.get("text")
    url = job.get("hostedUrl")

    if not title or not url:
        return None

    if not is_valid_job_text(title):
        return None

    return {
        "title": title,
        "company": board,
        "description": "Lever ATS job",
        "link": url,
        "source": "lever",
        "date": datetime.now().strftime("%Y-%m-%d")
    }

# =========================================================
# DOM EXTRACTION (ROBUST + NON-STRICT)
# =========================================================

def extract_dom_jobs(html, company, base_url):

    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    # IMPORTANT: broader capture (fixes empty output problem)
    elements = soup.find_all(["a", "li", "div", "span"])

    for el in elements:

        text = el.get_text(" ", strip=True)

        if not is_valid_job_text(text):
            continue

        jobs.append({
            "title": text,
            "company": company,
            "description": "DOM extracted job",
            "link": base_url,
            "source": "dom",
            "date": datetime.now().strftime("%Y-%m-%d")
        })

    return jobs

# =========================================================
# CAREER PAGE RESOLUTION (SAFE + MULTI-PATH)
# =========================================================

def resolve_endpoints(firm):

    slug = firm.lower().replace(" ", "")

    return [
        f"https://boards.greenhouse.io/{slug}",
        f"https://jobs.lever.co/{slug}",
        f"https://{slug}.myworkdayjobs.com",
        f"https://careers.{slug}.com",
        f"https://www.{slug}.com/careers",
        f"https://www.{slug}.com/careers/jobs",
    ]

def fetch_from_firm(firm):

    endpoints = resolve_endpoints(firm)

    all_jobs = []

    for url in endpoints:

        html = safe_get(url, "text")

        if not html:
            continue

        jobs = extract_dom_jobs(html, firm, url)

        # IMPORTANT FIX:
        # no early return (this was breaking everything)
        if jobs:
            all_jobs.extend(jobs)

    return all_jobs

# =========================================================
# FALLBACK (ONLY IF ENTIRE SYSTEM FAILS)
# =========================================================

def fallback_jobs():
    return [{
        "title": "Director of Operations",
        "company": "RIA Market System",
        "description": "System fallback job",
        "link": "N/A",
        "source": "fallback",
        "date": datetime.now().strftime("%Y-%m-%d")
    }]

# =========================================================
# MASTER ENGINE
# =========================================================

def get_live_jobs():

    jobs = []

    # -------------------------
    # ATS LAYER
    # -------------------------
    for firm in RIA_FIRMS:

        slug = firm.lower().replace(" ", "")

        # Greenhouse
        for j in fetch_greenhouse(slug):
            job = normalize_greenhouse(j, slug)
            if job:
                jobs.append(job)

        # Lever
        for j in fetch_lever(slug):
            job = normalize_lever(j, slug)
            if job:
                jobs.append(job)

    # -------------------------
    # DOM LAYER
    # -------------------------
    for firm in RIA_FIRMS:
        jobs.extend(fetch_from_firm(firm))

    # -------------------------
    # FINAL SAFETY FALLBACK
    # -------------------------
    if len(jobs) == 0:
        return fallback_jobs()

    # -------------------------
    # DEDUP
    # -------------------------
    seen = set()
    cleaned = []

    for j in jobs:
        key = (j["title"], j["company"])
        if key not in seen:
            seen.add(key)
            cleaned.append(j)

    return cleaned
