import requests
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import json

# =========================================================
# SEED RIA UNIVERSE (STARTING POINT ONLY)
# =========================================================

RIA_SEED = [
    "Focus Financial Partners",
    "Hightower Advisors",
    "Commonwealth Financial Network",
    "LPL Financial",
    "Ameriprise Financial",
    "Raymond James",
    "Cetera Financial",
    "AssetMark",
    "Creative Planning",
    "Wealth Enhancement Group",
]

# =========================================================
# RIA EXPANSION KEYWORDS (DISCOVERY LAYER)
# =========================================================

RIA_DISCOVERY_QUERIES = [
    "independent RIA wealth management careers",
    "registered investment advisor hiring operations",
    "wealth management firm advisor services jobs",
    "financial advisor platform operations careers",
    "RIA client service director jobs",
    "wealth advisory firm operations manager careers"
]

# =========================================================
# ATS SOURCES
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
# SAFE REQUEST
# =========================================================

def safe_get(url, mode="text"):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return None
        return r.json() if mode == "json" else r.text
    except:
        return None

# =========================================================
# RIA UNIVERSE EXPANSION ENGINE
# =========================================================

def expand_ria_universe():

    """
    Builds a dynamic RIA list beyond hardcoded firms.
    This is your coverage multiplier.
    """

    expanded = set(RIA_SEED)

    # Simulated expansion (no API dependency version)
    # In production this would be replaced with search ingestion
    discovery_pool = [
        "Mercer Advisors",
        "Mariner Wealth Advisors",
        "Carson Group",
        "Cambridge Investment Research",
        "Kestra Financial",
        "Baird Private Wealth",
        "Stifel Wealth Management",
        "UBS Wealth Management",
        "Morgan Stanley Wealth Management",
        "Edward Jones",
        "Northern Trust Wealth Management",
        "Edelman Financial Engines",
        "Mariner Platform Solutions",
        "Private Advisor Group",
        "Captrust Financial Advisors",
    ]

    for firm in discovery_pool:
        expanded.add(firm)

    return list(expanded)

# =========================================================
# JOB VALIDATION (BALANCED, NOT OVER-STRICT)
# =========================================================

EXCLUDE = [
    "contact", "privacy", "terms", "cookie",
    "life at", "culture", "about", "blog",
    "press", "news", "events", "insights"
]

INCLUDE = [
    "director", "vp", "vice president", "head",
    "manager", "lead", "operations",
    "client", "advisor", "wealth",
    "associate", "specialist", "consultant",
    "analyst", "relationship", "service"
]

def looks_valid(text):

    t = text.lower()

    if any(x in t for x in EXCLUDE):
        return False

    if not any(x in t for x in INCLUDE):
        return False

    if len(text.split()) < 2:
        return False

    return True

# =========================================================
# GREENHOUSE
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

    if not looks_valid(title):
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
# LEVER
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

    if not looks_valid(title):
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
# SIMPLE DOM EXTRACTION (SAFE MODE)
# =========================================================

def extract_dom_jobs(html, company, base_url):

    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    for a in soup.find_all("a", href=True):

        text = a.get_text(" ", strip=True)

        if not text:
            continue

        if not looks_valid(text):
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

def fetch_ria_dom(company, url):

    html = safe_get(url, "text")
    if not html:
        return []

    return extract_dom_jobs(html, company, url)

# =========================================================
# FALLBACK (ONLY IF EVERYTHING FAILS)
# =========================================================

def fallback_jobs():

    return [{
        "title": "Director of Operations",
        "company": "RIA Market (Fallback)",
        "description": "System fallback role",
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
    # EXPAND RIA UNIVERSE FIRST
    # -------------------------
    ria_universe = expand_ria_universe()

    # -------------------------
    # ATS INGESTION
    # -------------------------
    for board in GREENHOUSE_BOARDS:
        for j in fetch_greenhouse(board):
            job = normalize_greenhouse(j, board)
            if job:
                jobs.append(job)

    for board in LEVER_BOARDS:
        for j in fetch_lever(board):
            job = normalize_lever(j, board)
            if job:
                jobs.append(job)

    # -------------------------
    # DOM INGESTION ACROSS EXPANDED UNIVERSE
    # -------------------------
    for firm in ria_universe:

        # NOTE: generic guess endpoint (safe fallback pattern)
        url = f"https://www.{firm.lower().replace(' ', '')}.com/careers"

        jobs += fetch_ria_dom(firm, url)

    # -------------------------
    # FINAL FALLBACK SAFETY
    # -------------------------
    if len(jobs) == 0:
        jobs = fallback_jobs()

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
