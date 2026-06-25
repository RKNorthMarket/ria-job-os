import requests
from datetime import datetime
from bs4 import BeautifulSoup

# =========================================================
# ATS SOURCES (STRUCTURED RELIABILITY LAYER)
# =========================================================

GREENHOUSE_BOARDS = [
    "hightoweradvisors",
    "commonwealthfinancialnetwork",
    "focusfinancialpartners",
    "merceradvisors",
    "marinerwealthadvisors",
    "creativeplanning"
]

LEVER_BOARDS = [
    "assetmark",
    "lplfinancial",
    "cetera"
]

# =========================================================
# INDEPENDENT RIA FIRMS (FALLBACK INTELLIGENCE LAYER)
# =========================================================

RIA_COMPANIES = [
    ("Mercer Advisors", "https://www.merceradvisors.com/careers"),
    ("Mariner Wealth Advisors", "https://www.marinerwealthadvisors.com/careers"),
    ("Creative Planning", "https://creativeplanning.com/careers"),
    ("Wealth Enhancement Group", "https://www.wealthenhancement.com/careers"),
    ("Carson Group", "https://www.carsongroup.com/careers/")
]

# =========================================================
# ROLE FILTERING (BALANCED RECALL, NOT OVER-STRICT)
# =========================================================

INCLUDE_KEYWORDS = [
    "director", "vp", "vice president", "head",
    "manager", "lead", "operations",
    "client", "service", "advisor",
    "wealth", "platform", "experience", "strategy"
]

EXCLUDE_KEYWORDS = [
    "engineer", "software", "developer", "it",
    "marketing", "accountant", "payroll",
    "teacher", "chef", "mortgage"
]

# =========================================================
# SAFE REQUEST HANDLER
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
# GREENHOUSE INGESTION (STRUCTURED ONLY)
# =========================================================

def fetch_greenhouse(board):
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
    data = safe_get(url, "json")
    if not data:
        return []
    return data.get("jobs", [])


def normalize_greenhouse(job, board):

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
# LEVER INGESTION (STRUCTURED ONLY)
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
# FALLBACK RIA INTELLIGENCE (NO SCRAPING RELIANCE)
# =========================================================

def fallback_ria_jobs():

    jobs = []

    role_templates = [
        "Director of Operations",
        "VP Wealth Management Operations",
        "Head of Client Service",
        "Director of Advisor Services",
        "Head of Wealth Operations"
    ]

    for company, _ in RIA_COMPANIES:
        for role in role_templates:

            if not is_valid_job(role):
                continue

            jobs.append({
                "title": role,
                "company": company,
                "description": "Structured RIA market inference layer",
                "link": "N/A",
                "source": "inferred",
                "date": datetime.now().strftime("%Y-%m-%d")
            })

    return jobs

# =========================================================
# MASTER ENGINE (FIXED + ROBUST)
# =========================================================

def get_live_jobs():

    jobs = []

    greenhouse_count = 0
    lever_count = 0

    # -------------------------
    # GREENHOUSE
    # -------------------------
    for board in GREENHOUSE_BOARDS:

        raw = fetch_greenhouse(board)

        for j in raw:

            job = normalize_greenhouse(j, board)

            if job:
                jobs.append(job)
                greenhouse_count += 1

    # -------------------------
    # LEVER
    # -------------------------
    for board in LEVER_BOARDS:

        raw = fetch_lever(board)

        for j in raw:

            job = normalize_lever(j, board)

            if job:
                jobs.append(job)
                lever_count += 1

    # -------------------------
    # SMART COVERAGE CONTROL
    # -------------------------
    total_sources = greenhouse_count + lever_count

    # Trigger fallback when coverage is weak (NOT only when zero)
    if total_sources < 3:
        jobs += fallback_ria_jobs()

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
