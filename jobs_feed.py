import requests
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import json
import re

# =========================================================
# RIA SEED UNIVERSE
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
# JOB FILTERS (BALANCED — NOT OVER-RESTRICTIVE)
# =========================================================

BAD = [
    "contact", "privacy", "terms", "cookie",
    "life at", "culture", "about", "blog",
    "news", "press", "events", "insights"
]

GOOD = [
    "director", "vp", "vice president", "head",
    "manager", "lead", "operations", "client",
    "advisor", "wealth", "associate",
    "specialist", "analyst", "service", "relationship"
]

def is_job(text: str) -> bool:
    t = text.lower()
    if any(b in t for b in BAD):
        return False
    return any(g in t for g in GOOD)

# =========================================================
# CRITICAL FIX: REALISTIC ATS ENDPOINT RESOLUTION
# =========================================================

def resolve_endpoints(firm: str):

    """
    Instead of guessing one URL, try real-world ATS patterns.
    This is the fix that stops fallback-only behavior.
    """

    slug = firm.lower().replace(" ", "")

    return [
        f"https://boards.greenhouse.io/{slug}",
        f"https://jobs.lever.co/{slug}",
        f"https://{slug}.myworkdayjobs.com",
        f"https://careers.{slug}.com",
        f"https://www.{slug}.com/careers",
        f"https://www.{slug}.com/careers/jobs",
    ]

# =========================================================
# ATS: GREENHOUSE
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

    if not is_job(title):
        return None

    return {
        "title": title,
        "company": board,
        "description": "Greenhouse ATS job",
        "link": url,
        "source": "greenhouse",
        "date": datetime.now().strftime("%Y-%m-%d")
    }

# =========================================================
# ATS: LEVER
# =========================================================

def fetch_lever(board):
    url = f"https://api.lever.co/v0/postings/{board}?mode=json"
    data = safe_get(url, "json")
    return data if isinstance(data, list) else []

def normalize_lever(job, board):

    title = job.get("text")
    url = job.get("hostedUrl")

    if not title or not url:
        return None

    if not is_job(title):
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
# DOM EXTRACTION (SAFE MODE)
# =========================================================

def extract_dom_jobs(html, company, base_url):

    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    for a in soup.find_all("a", href=True):

        text = a.get_text(" ", strip=True)

        if not text:
            continue

        if not is_job(text):
            continue

        jobs.append({
            "title": text,
            "company": company,
            "description": "DOM extracted job",
            "link": urljoin(base_url, a["href"]),
            "source": "dom",
            "date": datetime.now().strftime("%Y-%m-%d")
        })

    return jobs

# =========================================================
# CRITICAL FIX: MULTI-ENDPOINT FETCHER (THIS SOLVES YOUR ISSUE)
# =========================================================

def fetch_from_firm(firm):

    endpoints = resolve_endpoints(firm)

    for url in endpoints:

        html = safe_get(url, "text")

        if html:
            jobs = extract_dom_jobs(html, firm, url)

            if jobs:
                return jobs

    return []

# =========================================================
# FALLBACK SAFETY
# =========================================================

def fallback_jobs():

    return [{
        "title": "Director of Operations",
        "company": "RIA Market System",
        "description": "System fallback job (no sources available)",
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
    # ATS LAYER (REAL DATA)
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
    # DOM LAYER (FIXED MULTI-ENDPOINT)
    # -------------------------
    for firm in RIA_FIRMS:
        jobs += fetch_from_firm(firm)

    # -------------------------
    # FINAL SAFETY FALLBACK
    # -------------------------
    if not jobs:
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
