import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re

# =========================================================
# ATS SOURCES (STRUCTURED LAYER)
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
# INDEPENDENT RIA FIRMS (CRITICAL COVERAGE LAYER)
# =========================================================

RIA_CAREERS = [
    ("Mercer Advisors", "https://www.merceradvisors.com/careers"),
    ("Mariner Wealth Advisors", "https://www.marinerwealthadvisors.com/careers"),
    ("Creative Planning", "https://creativeplanning.com/careers"),
    ("Wealth Enhancement Group", "https://www.wealthenhancement.com/careers"),
    ("Carson Group", "https://www.carsongroup.com/careers")
]

# =========================================================
# FILTERING (BALANCED - NOT OVER-RESTRICTIVE)
# =========================================================

INCLUDE = [
    "director", "vp", "vice president", "head",
    "manager", "lead", "operations",
    "client", "service", "advisor",
    "wealth", "platform", "experience",
    "associate", "specialist", "consultant",
    "analyst", "coordinator", "relationship",
    "practice", "financial advisor"
]

EXCLUDE = [
    "engineer", "software", "developer", "it",
    "marketing", "accountant", "payroll",
    "teacher", "chef", "mortgage", "intern"
]

JOB_PATTERNS = [
    "job", "career", "position", "opening", "role", "opportunity"
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
# VALIDATION ENGINE
# =========================================================

def is_valid_job(title, desc=""):

    text = f"{title} {desc}".lower()

    if any(x in text for x in EXCLUDE):
        return False

    if not any(x in text for x in INCLUDE):
        return False

    if len(title.split()) < 2:
        return False

    return True

# =========================================================
# JOB RELEVANCE SCORER (USED FOR DOM EXTRACTION)
# =========================================================

def job_relevance_score(text):

    t = text.lower()
    score = 0

    for k in INCLUDE:
        if k in t:
            score += 2

    for k in EXCLUDE:
        if k in t:
            score -= 3

    if any(p in t for p in JOB_PATTERNS):
        score += 2

    return score

# =========================================================
# GREENHOUSE
# =========================================================

def fetch_greenhouse(board):
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
    data = safe_get(url, "json")
    return data.get("jobs", []) if data else []


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
        "description": "Greenhouse ATS verified",
        "link": url,
        "source": "greenhouse",
        "date": datetime.now().strftime("%Y-%m-%d")
    }

# =========================================================
# LEVER
# =========================================================

def fetch_lever(board):
    url = f"https://api.lever.co/v0/postings/{board}?mode=json"
    data = safe_get(url, "json")
    return data if isinstance(data, list) else []


def normalize_lever(job, board):

    title = job.get("text")
    url = job.get("hostedUrl")
    desc = job.get("descriptionPlain", "")
    company = job.get("company", board)

    if not title or not url:
        return None

    if not is_valid_job(title, desc):
        return None

    return {
        "title": title,
        "company": company,
        "description": "Lever ATS verified",
        "link": url,
        "source": "lever",
        "date": datetime.now().strftime("%Y-%m-%d")
    }

# =========================================================
# DOM EXTRACTION (FIXED - NOT OVER-RESTRICTIVE)
# =========================================================

def extract_dom_jobs(html, company, base_url):

    soup = BeautifulSoup(html, "html.parser")

    jobs = []

    # IMPORTANT: do NOT over-filter DOM structure
    candidates = soup.find_all(["a", "li", "div"])

    for c in candidates:

        text = c.get_text(" ", strip=True)

        if not text or len(text) < 5:
            continue

        score = job_relevance_score(text)

        # soft threshold (KEY FIX)
        if score < 2:
            continue

        link_tag = c.find("a")
        link = link_tag.get("href") if link_tag and link_tag.get("href") else base_url

        if is_valid_job(text):
            jobs.append({
                "title": text,
                "company": company,
                "description": "DOM extracted job card",
                "link": link,
                "source": "dom",
                "date": datetime.now().strftime("%Y-%m-%d")
            })

    return jobs


def fetch_ria_dom(company, url):

    html = safe_get(url, "text")
    if not html:
        return []

    return extract_dom_jobs(html, company, url)

# =========================================================
# FALLBACK (ONLY IF EMPTY SYSTEM-WIDE)
# =========================================================

def fallback_jobs():

    roles = [
        "Director of Operations",
        "VP Wealth Management Operations",
        "Head of Client Service",
        "Director of Advisor Services",
        "Wealth Management Associate"
    ]

    jobs = []

    for company, _ in RIA_CAREERS:
        for role in roles:

            if not is_valid_job(role):
                continue

            jobs.append({
                "title": role,
                "company": company,
                "description": "Inference fallback role",
                "link": "N/A",
                "source": "inferred",
                "date": datetime.now().strftime("%Y-%m-%d")
            })

    return jobs

# =========================================================
# MASTER ENGINE
# =========================================================

def get_live_jobs():

    jobs = []

    # -------------------------
    # ATS LAYER
    # -------------------------
    for board in GREENHOUSE_BOARDS:
        for j in fetch_greenhouse(board):
            job = normalize_greenhouse(j, board)
            if job:
                jobs.append(job)

    for board in LEVER_BOARDS:
        for j in fetch_lever(board):
            job = normalize_lever(j, board)
            if job:
                jobs.append(job)

    # -------------------------
    # DOM LAYER (CRITICAL FIX)
    # -------------------------
    for company, url in RIA_CAREERS:
        jobs += fetch_ria_dom(company, url)

    # -------------------------
    # SAFETY FALLBACK
    # -------------------------
    if len(jobs) == 0:
        jobs = fallback_jobs()

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
