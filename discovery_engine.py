import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime

# =========================================================
# JOB SURFACE SOURCES (NOT FIRMS)
# =========================================================

JOB_SURFACE_QUERIES = [
    "wealth management careers operations manager",
    "RIA client service jobs apply",
    "site:boards.greenhouse.io advisor operations",
    "site:jobs.lever.co wealth management",
    "Workday financial services jobs",
    "asset management operations careers"
]

# =========================================================
# SAFE FETCH
# =========================================================

def safe_get(url):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return None
        return r.text
    except:
        return None

# =========================================================
# STEP 1: DISCOVER JOB SURFACES (NOT COMPANIES)
# =========================================================

def discover_job_surfaces():

    """
    Finds job pages first, companies second.
    """

    surfaces = set()

    for q in JOB_SURFACE_QUERIES:

        url = f"https://www.bing.com/search?q={q}"
        html = safe_get(url)

        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")

        for a in soup.find_all("a", href=True):

            href = a["href"]

            if any(x in href.lower() for x in [
                "greenhouse",
                "lever",
                "workday",
                "jobs",
                "careers",
                "icims",
                "ashby"
            ]):
                surfaces.add(href)

    return list(surfaces)

# =========================================================
# STEP 2: EXTRACT JOB LINKS ONLY
# =========================================================

JOB_HINTS = [
    "/job", "/jobs", "/careers", "/posting", "/position", "jobId"
]

BAD_HINTS = [
    "privacy", "cookie", "terms", "about", "life", "blog", "news", "contact"
]

def is_job_link(text):

    t = text.lower()

    if any(b in t for b in BAD_HINTS):
        return False

    return any(j in t for j in JOB_HINTS)

# =========================================================
# STEP 3: EXTRACT JOBS FROM SURFACE
# =========================================================

def extract_jobs(surface_url):

    html = safe_get(surface_url)

    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")

    jobs = []

    for a in soup.find_all("a", href=True):

        title = a.get_text(" ", strip=True)

        if len(title) < 6:
            continue

        if not is_job_link(a["href"]) and not is_job_link(title):
            continue

        jobs.append({
            "title": title,
            "company": infer_company(surface_url),
            "link": urljoin(surface_url, a["href"]),
            "source": "job_surface",
            "date": datetime.now().strftime("%Y-%m-%d")
        })

    return jobs

# =========================================================
# STEP 4: INFER COMPANY FROM DOMAIN
# =========================================================

def infer_company(url):

    try:
        domain = urlparse(url).netloc
        return domain.replace("www.", "")
    except:
        return "unknown"

# =========================================================
# MASTER ENGINE
# =========================================================

def get_surface_jobs():

    surfaces = discover_job_surfaces()

    all_jobs = []

    for s in surfaces:
        all_jobs.extend(extract_jobs(s))

    # dedup
    seen = set()
    cleaned = []

    for j in all_jobs:
        key = (j["title"], j["company"])

        if key not in seen:
            seen.add(key)
            cleaned.append(j)

    return cleaned
