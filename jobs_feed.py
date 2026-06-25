import requests
from datetime import datetime
from urllib.parse import urljoin

# =========================================================
# EXPANDED RIA UNIVERSE (still seed-based but broader)
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
    "Baird Private Wealth",
    "Edelman Financial Engines",
    "Private Advisor Group",
    "Kestra Financial",
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
# JOB SIGNAL DETECTION (STRUCTURAL ONLY)
# =========================================================

JOB_URL_HINTS = [
    "/job", "/jobs", "/careers", "/posting", "/position"
]

def is_job_url(url: str) -> bool:
    u = url.lower()
    return any(h in u for h in JOB_URL_HINTS)

# =========================================================
# ATS INGESTION (PRIMARY SOURCE OF TRUTH)
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

    return {
        "title": title,
        "company": board,
        "description": "Lever ATS job",
        "link": url,
        "source": "lever",
        "date": datetime.now().strftime("%Y-%m-%d")
    }

# =========================================================
# STRICT JOB FILTER (ONLY AFTER INGESTION)
# =========================================================

def is_relevant_title(title: str) -> bool:

    t = title.lower()

    keywords = [
        "director", "vp", "vice president", "head",
        "manager", "lead", "operations", "client",
        "advisor", "wealth", "service",
        "associate", "specialist", "analyst"
    ]

    return any(k in t for k in keywords)

# =========================================================
# CAREERS PAGE DISCOVERY (NO CONTENT SCRAPING)
# =========================================================

def get_careers_page(firm):

    slug = firm.lower().replace(" ", "")
    return f"https://www.{slug}.com/careers"

def fetch_careers_links(firm):

    url = get_careers_page(firm)

    html = safe_get(url, "text")

    if not html:
        return []

    # ONLY extract job-like URLs (not page text)
    links = []

    for part in html.split('"'):
        if is_job_url(part):
            links.append(urljoin(url, part))

    return links

# =========================================================
# MASTER ENGINE
# =========================================================

def get_live_jobs():

    jobs = []

    # -------------------------
    # ATS LAYER (PRIMARY)
    # -------------------------
    for firm in RIA_FIRMS:

        slug = firm.lower().replace(" ", "")

        for j in fetch_greenhouse(slug):
            job = normalize_greenhouse(j, slug)
            if job:
                jobs.append(job)

        for j in fetch_lever(slug):
            job = normalize_lever(j, slug)
            if job:
                jobs.append(job)

    # -------------------------
    # CAREER PAGE LAYER (STRUCTURED ONLY)
    # -------------------------
    for firm in RIA_FIRMS:

        links = fetch_careers_links(firm)

        for link in links:

            title = link.split("/")[-1].replace("-", " ").title()

            if is_relevant_title(title):
                jobs.append({
                    "title": title,
                    "company": firm,
                    "description": "Structured careers link job",
                    "link": link,
                    "source": "discovered",
                    "date": datetime.now().strftime("%Y-%m-%d")
                })

    # -------------------------
    # FINAL SAFETY
    # -------------------------
    if not jobs:
        return [{
            "title": "Director of Operations",
            "company": "RIA Market System",
            "description": "Fallback safety job",
            "link": "N/A",
            "source": "fallback",
            "date": datetime.now().strftime("%Y-%m-%d")
        }]

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
