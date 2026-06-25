import requests
from datetime import datetime
from bs4 import BeautifulSoup

# =========================================================
# ROLE INTELLIGENCE FILTERS
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
# INDEPENDENT RIA FIRMS (NO RELY ON LINK SCRAPING STRUCTURE)
# =========================================================

RIA_CAREERS = [
    ("Mercer Advisors", "https://www.merceradvisors.com/careers/"),
    ("Mariner Wealth Advisors", "https://www.marinerwealthadvisors.com/careers/"),
    ("Creative Planning", "https://creativeplanning.com/careers/"),
    ("Wealth Enhancement Group", "https://www.wealthenhancement.com/careers")
]

# =========================================================
# SAFE REQUEST HELPERS
# =========================================================

def safe_get_json(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None


def safe_get_html(url):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return None
        return r.text
    except:
        return None

# =========================================================
# STRICT VALIDATION (CORE FIX)
# =========================================================

def is_valid_job_text(text):

    if not text:
        return False

    t = text.lower()

    # kill marketing / nav noise
    noise = [
        "call us", "learn more", "read more",
        "contact us", "our services",
        "investment management", "tax strategies",
        "locations", "about us"
    ]

    if any(n in t for n in noise):
        return False

    if any(b in t for b in EXCLUDE_KEYWORDS):
        return False

    if not any(i in t for i in INCLUDE_KEYWORDS):
        return False

    # must be job-like length
    if len(t.split()) < 3:
        return False

    return True

# =========================================================
# GREENHOUSE INGESTION
# =========================================================

def fetch_greenhouse(board):
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
    data = safe_get_json(url)
    if not data:
        return []
    return data.get("jobs", [])


def normalize_greenhouse(job, board):

    return {
        "title": job.get("title", ""),
        "company": job.get("company_name", board),
        "description": job.get("content", ""),
        "link": job.get("absolute_url", ""),
        "source": "greenhouse"
    }

# =========================================================
# LEVER INGESTION
# =========================================================

def fetch_lever(board):
    url = f"https://api.lever.co/v0/postings/{board}?mode=json"
    data = safe_get_json(url)
    return data if isinstance(data, list) else []


def normalize_lever(job, board):

    return {
        "title": job.get("text", ""),
        "company": job.get("company", board),
        "description": job.get("descriptionPlain", ""),
        "link": job.get("hostedUrl", ""),
        "source": "lever"
    }

# =========================================================
# RIA CAREER PAGE EXTRACTION (CONTROLLED)
# =========================================================

def extract_job_cards(html, company, base_url):

    soup = BeautifulSoup(html, "html.parser")

    jobs = []

    # ONLY look for structured job-like elements
    candidates = soup.find_all(["a", "li", "div"])

    for c in candidates:

        text = c.get_text(" ", strip=True)

        if not is_valid_job_text(text):
            continue

        # attempt to extract link safely
        a = c.find("a")
        link = None

        if a and a.get("href"):
            link = a.get("href")
        else:
            link = base_url

        jobs.append({
            "title": text,
            "company": company,
            "description": "RIA career page verified posting",
            "link": link,
            "source": "ria_direct"
        })

    return jobs


def scrape_ria_company(company, url):

    html = safe_get_html(url)
    if not html:
        return []

    return extract_job_cards(html, company, url)

# =========================================================
# MASTER INGESTION ENGINE
# =========================================================

def get_live_jobs():

    jobs = []

    # -------------------------
    # GREENHOUSE
    # -------------------------
    for board in GREENHOUSE_BOARDS:
        raw = fetch_greenhouse(board)

        for j in raw:
            job = normalize_greenhouse(j, board)

            if is_valid_job_text(job["title"] + job["description"]):
                jobs.append(job)

    # -------------------------
    # LEVER
    # -------------------------
    for board in LEVER_BOARDS:
        raw = fetch_lever(board)

        for j in raw:
            job = normalize_lever(j, board)

            if is_valid_job_text(job["title"] + job["description"]):
                jobs.append(job)

    # -------------------------
    # INDEPENDENT RIA FIRMS
    # -------------------------
    for company, url in RIA_CAREERS:
        jobs += scrape_ria_company(company, url)

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
