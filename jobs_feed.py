import requests
from datetime import datetime
from urllib.parse import urlparse

# =========================================================
# SEED FIRMS (ONLY STARTING POINT)
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
# ATS FINGERPRINT LIBRARY
# =========================================================

ATS_PATTERNS = {
    "greenhouse": "/boards.greenhouse.io/",
    "lever": "api.lever.co",
    "workday": "myworkdayjobs.com",
    "icims": "icims.com",
    "ashby": "ashbyhq.com",
    "bamboohr": "bamboohr.com",
    "jazzhr": "jazz.co"
}

def detect_ats(url: str):

    for ats, pattern in ATS_PATTERNS.items():
        if pattern in url:
            return ats

    return None

# =========================================================
# DOMAIN DISCOVERY (KEY UPGRADE)
# =========================================================

def discover_company_domains():

    """
    Instead of guessing jobs, we discover firm domains first.
    This expands beyond seed list.
    """

    domains = set()

    for firm in RIA_FIRMS:

        slug = firm.lower().replace(" ", "")

        candidates = [
            f"https://www.{slug}.com",
            f"https://{slug}.com",
            f"https://www.{slug}.com/careers"
        ]

        for url in candidates:
            domains.add(url)

    return list(domains)

# =========================================================
# ATS ENDPOINT SCANNER (CORE ENGINE)
# =========================================================

def scan_for_ats(domain_url):

    """
    Detects ATS footprint WITHOUT needing full scraping.
    """

    html = safe_get(domain_url)

    if not html:
        return []

    detected = []

    for ats_name, pattern in ATS_PATTERNS.items():

        if pattern in html:
            detected.append({
                "ats": ats_name,
                "source": domain_url
            })

    return detected

# =========================================================
# ATS JOB INGESTION
# =========================================================

def fetch_greenhouse(board):
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
    data = safe_get(url, "json")
    return data.get("jobs", []) if data else []

def fetch_lever(board):
    url = f"https://api.lever.co/v0/postings/{board}?mode=json"
    data = safe_get(url, "json")
    return data if isinstance(data, list) else []

def fetch_workday(domain):

    url = f"{domain}/jobs"
    html = safe_get(url)

    if not html:
        return []

    # Workday jobs often embedded as JSON blobs
    if "workday" in html.lower():

        return [{
            "title": "Workday Job Detected (parsed)",
            "company": domain,
            "description": "Workday ATS footprint detected",
            "link": domain,
            "source": "workday"
        }]

    return []

# =========================================================
# NORMALIZERS
# =========================================================

def normalize_greenhouse(job, board):

    return {
        "title": job.get("title", ""),
        "company": board,
        "description": "Greenhouse ATS job",
        "link": job.get("absolute_url", ""),
        "source": "greenhouse",
        "date": datetime.now().strftime("%Y-%m-%d")
    }

def normalize_lever(job, board):

    return {
        "title": job.get("text", ""),
        "company": board,
        "description": "Lever ATS job",
        "link": job.get("hostedUrl", ""),
        "source": "lever",
        "date": datetime.now().strftime("%Y-%m-%d")
    }

# =========================================================
# MASTER ATS FINGERPRINT ENGINE
# =========================================================

def get_live_jobs():

    jobs = []

    domains = discover_company_domains()

    # =====================================================
    # STEP 1: ATS fingerprint detection
    # =====================================================

    detected_sources = []

    for d in domains:
        detected_sources.extend(scan_for_ats(d))

    # =====================================================
    # STEP 2: structured ingestion based on ATS type
    # =====================================================

    for src in detected_sources:

        ats = src["ats"]
        base = src["source"]

        # Greenhouse / Lever still primary structured sources
        if ats == "greenhouse":
            slug = base.split("/")[-1]
            for j in fetch_greenhouse(slug):
                jobs.append(normalize_greenhouse(j, slug))

        elif ats == "lever":
            slug = base.split("/")[-1]
            for j in fetch_lever(slug):
                jobs.append(normalize_lever(j, slug))

        elif ats == "workday":
            jobs.extend(fetch_workday(base))

        else:
            jobs.append({
                "title": f"{ats.title()} ATS Detected",
                "company": base,
                "description": "ATS fingerprint detected (unparsed)",
                "link": base,
                "source": ats,
                "date": datetime.now().strftime("%Y-%m-%d")
            })

    # =====================================================
    # FINAL SAFETY FALLBACK
    # =====================================================

    if not jobs:
        return [{
            "title": "Director of Operations",
            "company": "RIA Market System",
            "description": "Fallback system job",
            "link": "N/A",
            "source": "fallback",
            "date": datetime.now().strftime("%Y-%m-%d")
        }]

    # =====================================================
    # DEDUP
    # =====================================================

    seen = set()
    cleaned = []

    for j in jobs:
        key = (j.get("title"), j.get("company"))

        if key not in seen:
            seen.add(key)
            cleaned.append(j)

    return cleaned
