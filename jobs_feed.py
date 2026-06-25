import json
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# =========================================================
# STRUCTURED DOM JOB EXTRACTION (FIXED VERSION)
# =========================================================

def extract_structured_jobs(html, company, base_url):

    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    # -----------------------------------------------------
    # 1. JSON-LD JOB OBJECTS (HIGHEST QUALITY SOURCE)
    # -----------------------------------------------------
    scripts = soup.find_all("script", type="application/ld+json")

    for s in scripts:
        try:
            if not s.string:
                continue

            data = json.loads(s.string)

            items = data if isinstance(data, list) else [data]

            for item in items:

                if not isinstance(item, dict):
                    continue

                if item.get("@type") not in ["JobPosting", "Job"]:
                    continue

                title = item.get("title")
                url = item.get("url") or base_url
                desc = item.get("description", "")

                if title:
                    jobs.append({
                        "title": title,
                        "company": company,
                        "description": "Structured JSON-LD job posting",
                        "link": urljoin(base_url, url),
                        "source": "jsonld",
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })

        except:
            continue

    # -----------------------------------------------------
    # 2. LINK-BASED JOB EXTRACTION (SAFE MODE ONLY)
    # -----------------------------------------------------

    noise_keywords = [
        "contact", "about", "life at", "culture",
        "benefits", "privacy", "terms", "login",
        "insights", "blog", "news", "events"
    ]

    links = soup.find_all("a", href=True)

    for a in links:

        text = a.get_text(" ", strip=True)
        href = a["href"]

        if not text or len(text) < 5:
            continue

        t = text.lower()

        # ❌ REMOVE MARKETING / NAVIGATION
        if any(n in t for n in noise_keywords):
            continue

        # ❌ REQUIRE JOB SIGNALS
        if not any(k in t for k in INCLUDE):
            continue

        # weak structural filter (not strict)
        if len(text.split()) < 2:
            continue

        jobs.append({
            "title": text,
            "company": company,
            "description": "DOM-extracted job listing",
            "link": urljoin(base_url, href),
            "source": "dom",
            "date": datetime.now().strftime("%Y-%m-%d")
        })

    return jobs


# =========================================================
# RIA DOM ENTRY POINT (REPLACE OLD FUNCTION)
# =========================================================

def fetch_ria_dom(company, url):

    html = safe_get(url, "text")

    if not html:
        return []

    return extract_structured_jobs(html, company, url)
