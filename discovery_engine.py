import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime

# =========================================================
# JOB SURFACE DISCOVERY QUERIES
# =========================================================

QUERIES = [
    "wealth management operations jobs",
    "RIA client service manager jobs",
    "site:lever.co wealth management",
    "site:boards.greenhouse.io advisor operations",
    "financial services operations careers",
]

def safe_get(url):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return None
        return r.text
    except:
        return None

# =========================================================
# DISCOVER JOB SURFACES
# =========================================================

def discover_surfaces():

    urls = set()

    for q in QUERIES:

        html = safe_get(f"https://www.bing.com/search?q={q}")
        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]

            if any(x in href for x in ["greenhouse", "lever", "workday", "jobs", "careers"]):
                urls.add(href)

    return list(urls)

# =========================================================
# JOB EXTRACTION
# =========================================================

def extract_jobs(url):

    html = safe_get(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")

    jobs = []

    for a in soup.find_all("a", href=True):

        title = a.get_text(strip=True)

        if len(title) < 6:
            continue

        if any(x in title.lower() for x in ["privacy", "cookie", "about", "contact", "life"]):
            continue

        jobs.append({
            "title": title,
            "company": infer_company(url),
            "link": urljoin(url, a["href"]),
            "source": "surface",
            "date": datetime.now().strftime("%Y-%m-%d")
        })

    return jobs

# =========================================================
# INFER COMPANY
# =========================================================

def infer_company(url):
    try:
        return urlparse(url).netloc.replace("www.", "")
    except:
        return "unknown"

# =========================================================
# MAIN ENTRYPOINT
# =========================================================

def get_surface_jobs():

    surfaces = discover_surfaces()

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
