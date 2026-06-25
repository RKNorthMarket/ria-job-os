import requests
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re

# =========================================================
# SEED FIRMS (ONLY BOOTSTRAP, NOT PRIMARY SOURCE)
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
]

# =========================================================
# SAFE HTTP
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
# JOB SIGNAL DETECTION
# =========================================================

JOB_KEYWORDS = [
    "director", "vp", "vice president", "head",
    "manager", "lead", "operations", "client",
    "advisor", "wealth", "service",
    "associate", "specialist", "analyst"
]

BAD_KEYWORDS = [
    "privacy", "cookie", "terms",
    "contact", "about", "life at",
    "culture", "blog", "press", "news"
]

def is_job_text(text: str) -> bool:
    t = text.lower()

    if len(text) < 6:
        return False

    if any(b in t for b in BAD_KEYWORDS):
        return False

    return any(k in t for k in JOB_KEYWORDS)

# =========================================================
# SEARCH-BASED DISCOVERY LAYER (CORE UPGRADE)
# =========================================================

def discover_ria_job_pages():

    """
    Instead of relying on known firms,
    we discover job boards via search patterns.
    """

    queries = [
        "site:boards.greenhouse.io wealth advisor jobs",
        "site:jobs.lever.co wealth operations",
        "wealth management careers apply",
        "RIA firm careers operations manager",
        "private wealth advisor careers jobs"
    ]

    discovered_urls = set()

    for q in queries:

        url = f"https://www.bing.com/search?q={q}"
        html = safe_get(url)

        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")

        for a in soup.find_all("a", href=True):

            href = a["href"]

            if any(x in href for x in ["greenhouse", "lever", "workday", "job"]):
                discovered_urls.add(href)

    return list(discovered_urls)

# =========================================================
# ATS INGESTION (TRUSTED SOURCE LAYER)
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
# DOM JOB EXTRACTION (JOB-FIRST ONLY)
# =========================================================

def extract_jobs_from_page(html, base_url):

    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    for a in soup.find_all("a", href=True):

        text = a.get_text(" ", strip=True)

        if not is_job_text(text):
            continue

        jobs.append({
            "title": text,
            "company": infer_company_from_url(base_url),
            "description": "discovered job",
            "link": urljoin(base_url, a["href"]),
            "source": "discovery",
            "date": datetime.now().strftime("%Y-%m-%d")
        })

    return jobs

# =========================================================
# COMPANY INFERENCE (IMPORTANT FOR UNKNOWN RIAs)
# =========================================================

def infer_company_from_url(url: str):

    try:
        domain = urlparse(url).netloc
        return domain.replace("www.", "")
    except:
        return "Unknown RIA"

# =========================================================
# SEARCH-DISCOVERED JOB SCRAPING
# =========================================================

def process_discovered_urls(urls):

    jobs = []

    for url in urls:

        html = safe_get(url)

        if not html:
            continue

        jobs.extend(extract_jobs_from_page(html, url))

    return jobs

# =========================================================
# SEED FALLBACK (ONLY SAFETY NET)
# =========================================================

def fallback_jobs():

    return [{
        "title": "Director of Operations",
        "company": "RIA Market System",
        "description": "Fallback system job",
        "link": "N/A",
        "source": "fallback",
        "date": datetime.now().strftime("%Y-%m-%d")
    }]

# =========================================================
# MASTER ENGINE (DISCOVERY-FIRST ARCHITECTURE)
# =========================================================

def get_live_jobs():

    jobs = []

    # -------------------------
    # 1. ATS INGESTION (HIGH SIGNAL)
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
    # 2. SEARCH DISCOVERY LAYER (NEW CORE)
    # -------------------------
    discovered_urls = discover_ria_job_pages()
    jobs.extend(process_discovered_urls(discovered_urls))

    # -------------------------
    # 3. FINAL SAFETY
    # -------------------------
    if not jobs:
        return fallback_jobs()

    # -------------------------
    # 4. DEDUP
    # -------------------------
    seen = set()
    cleaned = []

    for j in jobs:
        key = (j["title"], j["company"])

        if key not in seen:
            seen.add(key)
            cleaned.append(j)

    return cleaned
