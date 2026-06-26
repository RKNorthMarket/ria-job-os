import requests
from collections import defaultdict

# =========================================================
# ATS SOURCES
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
# ATS FETCHERS
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
# JOB SURFACE INGESTION
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
# UNKNOWN RIA INFERENCE (CORRECTED LOGIC)
# =========================================================

def detect_unknown_rias(jobs):

    """
    Correct logic:
    - NO domain clustering
    - NO ATS grouping
    - ONLY semantic job clustering by company field
    """

    firm_map = defaultdict(list)

    for j in jobs:

        company = j.get("company", "unknown")

        # filter junk keys
        if not company:
            continue

        firm_map[company].append(j)

    inferred = []

    for company, items in firm_map.items():

        text = " ".join([i.get("title","") for i in items]).lower()

        score = 0

        # semantic RIA signals
        if "advisor" in text:
            score += 25
        if "wealth" in text:
            score += 20
        if "client" in text:
            score += 10
        if "operations" in text:
            score += 15
        if "financial" in text:
            score += 10

        # minimum signal threshold
        if len(items) < 2 and score < 40:
            continue

        inferred.append({
            "company": company,
            "job_count": len(items),
            "ria_likelihood": min(score, 100),
            "sample_jobs": items[:3],
            "source": "inferred_ria"
        })

    inferred.sort(key=lambda x: x["ria_likelihood"], reverse=True)

    return inferred

# =========================================================
# MASTER ENTRYPOINT
# =========================================================

def get_surface_jobs_with_inference():

    jobs = get_surface_jobs()
    inferred_rias = detect_unknown_rias(jobs)

    return {
        "jobs": jobs,
        "inferred_rias": inferred_rias
    }
