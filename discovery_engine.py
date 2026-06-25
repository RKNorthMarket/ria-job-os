import requests
from datetime import datetime
from urllib.parse import urlparse
from collections import defaultdict

# =========================================================
# ATS SOURCES (STABLE CORE INPUT)
# =========================================================

GREENHOUSE_BOARDS = [
    "hightoweradvisors",
    "focusfinancialpartners",
    "commonwealthfinancialnetwork",
    "marinerwealthadvisors"
]

LEVER_BOARDS = [
    "focusfinancialpartners",
    "marinerwealthadvisors"
]

# =========================================================
# SAFE REQUEST
# =========================================================

def safe_get(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# =========================================================
# ATS INGESTION
# =========================================================

def fetch_greenhouse(board):
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
    data = safe_get(url)
    return data.get("jobs", []) if data else []

def fetch_lever(board):
    url = f"https://api.lever.co/v0/postings/{board}?mode=json"
    data = safe_get(url)
    return data if isinstance(data, list) else []

# =========================================================
# JOB SURFACE COLLECTION (PRIMARY INPUT)
# =========================================================

def get_surface_jobs():

    jobs = []

    # Greenhouse
    for b in GREENHOUSE_BOARDS:
        for j in fetch_greenhouse(b):
            jobs.append({
                "title": j.get("title"),
                "company": b,
                "link": j.get("absolute_url"),
                "source": "greenhouse"
            })

    # Lever
    for b in LEVER_BOARDS:
        for j in fetch_lever(b):
            jobs.append({
                "title": j.get("text"),
                "company": b,
                "link": j.get("hostedUrl"),
                "source": "lever"
            })

    return jobs

# =========================================================
# STEP 1: EXTRACT COMPANY DOMAINS
# =========================================================

def extract_domains(jobs):

    domains = []

    for j in jobs:
        link = j.get("link", "")

        try:
            d = urlparse(link).netloc.replace("www.", "")
            if d:
                domains.append(d)
        except:
            continue

    return domains

# =========================================================
# STEP 2: UNKNOWN RIA DETECTION ENGINE
# =========================================================

def detect_unknown_rias(jobs):

    """
    Core innovation:
    clusters job sources by domain and infers "new RIAs"
    """

    domain_map = defaultdict(list)

    for j in jobs:
        link = j.get("link", "")

        try:
            domain = urlparse(link).netloc.replace("www.", "")
        except:
            continue

        domain_map[domain].append(j)

    inferred_firms = []

    for domain, items in domain_map.items():

        if len(items) < 1:
            continue

        # heuristics for "RIA-likeness"
        score = 0

        text_blob = " ".join([i.get("title","") for i in items]).lower()

        if "advisor" in text_blob:
            score += 20
        if "wealth" in text_blob:
            score += 20
        if "client" in text_blob:
            score += 10
        if "operations" in text_blob:
            score += 10
        if "financial" in text_blob:
            score += 10

        inferred_firms.append({
            "company": domain,
            "job_count": len(items),
            "ria_likelihood": min(score, 100),
            "sample_jobs": items[:3],
            "source": "inferred_ria"
        })

    # sort by likelihood
    inferred_firms.sort(key=lambda x: x["ria_likelihood"], reverse=True)

    return inferred_firms

# =========================================================
# FINAL OUTPUT LAYER
# =========================================================

def get_surface_jobs_with_inference():

    jobs = get_surface_jobs()
    inferred_rias = detect_unknown_rias(jobs)

    return {
        "jobs": jobs,
        "inferred_rias": inferred_rias
    }
