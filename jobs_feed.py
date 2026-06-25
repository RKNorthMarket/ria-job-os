import requests
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import json

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
# INDEPENDENT RIA CAREER PAGES
# =========================================================

RIA_CAREERS = [
    ("Mercer Advisors", "https://www.merceradvisors.com/careers"),
    ("Mariner Wealth Advisors", "https://www.marinerwealthadvisors.com/careers"),
    ("Creative Planning", "https://creativeplanning.com/careers"),
    ("Wealth Enhancement Group", "https://www.wealthenhancement.com/careers"),
    ("Carson Group", "https://www.carsongroup.com/careers")
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
# BASIC VALIDATION (light-touch, NOT over-filtered)
# =========================================================

EXCLUDE = [
    "contact", "privacy", "terms", "cookie",
    "life at", "culture", "about", "blog",
    "events", "insights", "press"
]

def looks_like_noise(text: str) -> bool:
    t = text.lower()
    return any(x in t for x in EXCLUDE)

def looks_like_job(text: str) -> bool:
    t = text.lower()
    keywords = [
        "director", "vp", "vice president", "head",
        "manager", "lead", "operations",
        "client", "advisor", "wealth",
        "associate", "specialist", "consultant",
        "analyst", "relationship", "service"
    ]
    return any(k in t for k in keywords)

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

    if looks_like_noise(title):
        return None

    if not looks_like_job(title):
        return None

    return {
        "title": title,
        "company": board,
        "description": "Greenhouse ATS listing",
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

    if looks_like_noise(title):
        return None

    if not looks_like_job(title):
        return None

    return {
        "title": title,
        "company": board,
        "description": "Lever ATS listing",
        "link": url,
        "source": "lever",
        "date": datetime.now().strftime("%Y-%m-%d")
    }

# =========================================================
# STRUCTURED DOM EXTRACTION (FIXED: NO MARKETING NOISE)
# =========================================================

def extract_dom_jobs(html, company, base_url):

    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    # -----------------------------------------------------
    # 1. JSON-LD JOB POSTINGS (HIGHEST SIGNAL)
    # -----------------------------------------------------
    scripts = soup.find_all("script", type="application/ld+json")

    for s in scripts:
        try:
            if not s.string:
                continue

            data = json.loads(s.string)
            items = data if isinstance(data, list) else [data]

            for item in items:
                if not isinstance(item, dict):
                    continue

                if item.get("@type") not in ["JobPosting", "Job"]:
                    continue

                title = item.get("title")
                url = item.get("url") or base_url

                if title and not looks_like_noise(title):
                    jobs.append({
                        "title": title,
                        "company": company,
                        "description": "JSON-LD job posting",
                        "link": urljoin(base_url, url),
                        "source": "jsonld",
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })

        except:
            continue

    # -----------------------------------------------------
    # 2. LINK-BASED FALLBACK (CONTROLLED)
    # -----------------------------------------------------
    for a in soup.find_all("a", href=True):

        text = a.get_text(" ", strip=True)
        href = a["href"]

        if not text or len(text) < 4:
            continue

        if looks_like_noise(text):
            continue

        if not looks_like_job(text):
            continue

        jobs.append({
            "title": text,
            "company": company,
            "description": "DOM extracted job listing",
            "link": urljoin(base_url, href),
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

    roles = [
        "Director of Operations",
        "VP Wealth Management Operations",
        "Head of Client Service",
        "Wealth Management Associate",
        "Advisor Services Manager"
    ]

    jobs = []

    for company, _ in RIA_CAREERS:
        for role in roles:
            jobs.append({
                "title": role,
                "company": company,
                "description": "Inference fallback role",
                "link": "N/A",
                "source": "inferred",
                "date": datetime.now().strftime("%Y-%m-%d")
            })

    return jobs

# =========================================================
# MASTER ENGINE
# =========================================================

def get_live_jobs():

    jobs = []

    # -------------------------
    # ATS LAYER
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
    # DOM LAYER (RIA COVERAGE RESTORATION)
    # -------------------------
    for company, url in RIA_CAREERS:
        jobs += fetch_ria_dom(company, url)

    # -------------------------
    # FINAL SAFETY FALLBACK
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
