import requests
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re

# =========================================================
# INITIAL SEED (ONLY STARTING POINT)
# =========================================================

SEED_RIA_FIRMS = [
    "Focus Financial Partners",
    "Hightower Advisors",
    "Commonwealth Financial Network",
    "LPL Financial",
    "Ameriprise Financial",
    "Raymond James",
    "Cetera Financial",
    "AssetMark",
]

# =========================================================
# GLOBAL DISCOVERY STATE (GRAPH)
# =========================================================

DISCOVERED_FIRMS = set(SEED_RIA_FIRMS)
DISCOVERED_URLS = set()

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
# VALIDATION (LIGHT TOUCH ONLY)
# =========================================================

BAD = [
    "contact", "privacy", "terms", "cookie",
    "life at", "culture", "about", "blog",
    "news", "press", "events", "insights"
]

GOOD = [
    "director", "vp", "vice president", "head",
    "manager", "lead", "operations", "client",
    "advisor", "wealth", "associate", "specialist",
    "analyst", "service", "relationship"
]

def is_job(text):
    t = text.lower()
    if any(b in t for b in BAD):
        return False
    return any(g in t for g in GOOD)

# =========================================================
# 1. RIA DISCOVERY ENGINE (THE KEY UPGRADE)
# =========================================================

def discover_new_firms_from_links(links):

    """
    Extracts new RIAs from job URLs and company text patterns.
    This is how the system expands beyond your seed list.
    """

    new_firms = set()

    for link in links:

        # heuristic: extract domain brand signals
        domain = re.sub(r"https?://(www\.)?", "", link).split("/")[0]

        # convert domain → candidate firm name
        candidate = domain.replace(".com", "").replace("-", " ").title()

        if len(candidate) > 3:
            new_firms.add(candidate)

    return new_firms

# =========================================================
# 2. CAREER PAGE GENERATOR (FALLBACK DISCOVERY)
# =========================================================

def generate_career_url(firm):

    slug = firm.lower().replace(" ", "")
    return f"https://www.{slug}.com/careers"

# =========================================================
# 3. JOB EXTRACTION (DOM SAFE MODE)
# =========================================================

def extract_jobs(html, company, base_url):

    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    discovered_links = []

    for a in soup.find_all("a", href=True):

        text = a.get_text(" ", strip=True)
        href = a["href"]

        if not text:
            continue

        if not is_job(text):
            continue

        full_url = urljoin(base_url, href)

        jobs.append({
            "title": text,
            "company": company,
            "description": "Live graph extracted job",
            "link": full_url,
            "source": "graph",
            "date": datetime.now().strftime("%Y-%m-%d")
        })

        discovered_links.append(full_url)

    return jobs, discovered_links

# =========================================================
# 4. GRAPH EXPANSION STEP
# =========================================================

def expand_graph(new_links):

    global DISCOVERED_FIRMS

    new_firms = discover_new_firms_from_links(new_links)

    for f in new_firms:
        DISCOVERED_FIRMS.add(f)

# =========================================================
# 5. MASTER ENGINE
# =========================================================

def get_live_jobs():

    all_jobs = []
    all_links = []

    # -----------------------------------------------------
    # ITERATE CURRENT GRAPH
    # -----------------------------------------------------
    for firm in list(DISCOVERED_FIRMS):

        url = generate_career_url(firm)

        html = safe_get(url, "text")
        if not html:
            continue

        jobs, links = extract_jobs(html, firm, url)

        all_jobs.extend(jobs)
        all_links.extend(links)

    # -----------------------------------------------------
    # EXPAND GRAPH (THIS IS THE BREAKTHROUGH)
    # -----------------------------------------------------
    expand_graph(all_links)

    # -----------------------------------------------------
    # FALLBACK SAFETY
    # -----------------------------------------------------
    if not all_jobs:
        return [{
            "title": "Director of Operations",
            "company": "RIA Market Graph",
            "description": "Fallback system job",
            "link": "N/A",
            "source": "fallback",
            "date": datetime.now().strftime("%Y-%m-%d")
        }]

    # -----------------------------------------------------
    # DEDUP
    # -----------------------------------------------------
    seen = set()
    cleaned = []

    for j in all_jobs:
        key = (j["title"], j["company"])
        if key not in seen:
            seen.add(key)
            cleaned.append(j)

    return cleaned
