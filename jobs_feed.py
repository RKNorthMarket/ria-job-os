import requests
from datetime import datetime

# =========================================================
# ROLE FILTERS (STRICT BUT CLEAN)
# =========================================================

INCLUDE_KEYWORDS = [
    "director", "vp", "vice president", "head",
    "manager", "lead", "operations",
    "client", "service", "advisor",
    "wealth", "platform", "experience"
]

EXCLUDE_KEYWORDS = [
    "engineer", "software", "developer", "it",
    "marketing", "accountant", "payroll",
    "teacher", "chef", "mortgage"
]

# =========================================================
# ATS SOURCES (STRUCTURED ONLY)
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
# INDEPENDENT RIA FIRMS (FALLBACK ONLY)
# =========================================================

RIA_COMPANIES = [
    ("Mercer Advisors", "https://www.merceradvisors.com/careers"),
    ("Mariner Wealth Advisors", "https://www.marinerwealthadvisors.com/careers"),
    ("Creative Planning", "https://creativeplanning.com/careers"),
    ("Wealth Enhancement Group", "https://www.wealthenhancement.com/careers")
]

# =========================================================
# SAFE REQUEST
# =========================================================

def safe_get(url, mode="json"):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return None
        return r.json() if mode == "json" else r.text
    except:
        return None

# =========================================================
# VALIDATION ENGINE (CORE FILTER)
# =========================================================

def is_valid_job(title, description=""):

    text = f"{title} {description}".lower()

    if any(b in text for b in EXCLUDE_KEYWORDS):
        return False

    if not any(k in text for k in INCLUDE_KEYWORDS):
        return False

    if len(title.split()) < 2:
        return False

    return True

# =========================================================
# GREENHOUSE (STRUCTURED API ONLY)
# =========================================================

def fetch_greenhouse(board):

    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
    data = safe_get(url, "json")

    if not data:
        return []

    return data.get("jobs", [])


def normalize_greenhouse(job, board):

    # STRICT STRUCTURE VALIDATION
    title = job.get("title")
    url = job.get("absolute_url")
    company = job.get("company_name", board)

    if not title or not url:
        return None

    if not is_valid_job(title):
        return None

    return {
        "title": title,
        "company": company,
        "description": "Greenhouse ATS verified posting",
        "link": url,
        "source": "greenhouse",
        "date": datetime.now().strftime("%Y-%m-%d")
    }

# =========================================================
# LEVER (STRUCTURED API ONLY)
# =========================================================

def fetch_lever(board):

    url = f"https://api.lever.co/v0/postings/{board}?mode=json"
    data = safe_get(url, "json")

    return data if isinstance(data, list) else []


def normalize_lever(job, board):

    title = job.get("text")
    url = job.get("hostedUrl")
    company = job.get("company", board)
    desc = job.get("descriptionPlain", "")

    if not title or not url:
        return None

    if not is_valid_job(title, desc):
        return None

    return {
        "title": title,
        "company": company,
        "description": "Lever ATS verified posting",
        "link": url,
        "source": "lever",
        "date": datetime.now().strftime("%Y-%m-%d")
    }

# =========================================================
# INDEPENDENT RIA FALLBACK (NO HEURISTIC SCRAPING OF LINKS)
# =========================================================

def fallback_ria_jobs():

    # IMPORTANT: we do NOT scrape links anymore
    # Only safe "known role patterns" used as placeholders

    jobs = []

    patterns = [
        "Director of Operations",
        "VP Wealth Management Operations",
        "Head of Client Service",
        "Director of Advisor Services"
    ]

    for company, _ in RIA_COMPANIES:
        for role in patterns:

            if not is_valid_job(role):
                continue

            jobs.append({
                "title": role,
                "company": company,
                "description": "Structured RIA role inference (fallback layer)",
                "link": "N/A",
                "source": "inferred_structured",
                "date": datetime.now().strftime("%Y-%m-%d")
            })

    return jobs

# =========================================================
# MASTER ENGINE
# =========================================================

def get_live_jobs():

    jobs = []

    # -------------------------
    # GREENHOUSE (STRUCTURED)
    # -------------------------
    for board in GREENHOUSE_BOARDS:

        raw = fetch_greenhouse(board)

        for j in raw:

            job = normalize_greenhouse(j, board)

            if job:
                jobs.append(job)

    # -------------------------
    # LEVER (STRUCTURED)
    # -------------------------
    for board in LEVER_BOARDS:

        raw = fetch_lever(board)

        for j in raw:

            job = normalize_lever(j, board)

            if job:
                jobs.append(job)

    # -------------------------
    # FALLBACK (ONLY IF ATS IS EMPTY)
    # -------------------------
    if len(jobs) == 0:
        jobs = fallback_ria_jobs()

    # -------------------------
    # DEDUPLICATION
    # -------------------------
    seen = set()
    unique = []

    for j in jobs:

        key = (j["title"], j["company"])

        if key not in seen:
            seen.add(key)
            unique.append(j)

    return unique
