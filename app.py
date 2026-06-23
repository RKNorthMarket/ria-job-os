import streamlit as st
import requests
import urllib.parse

st.title("🧠 RIA Executive Job OS (Hybrid Intelligence Engine v8)")

st.write("""
This system combines:

✔ ATS ingestion (Greenhouse + Lever)  
✔ LinkedIn discovery layer (search-based, not scraping)  
✔ RIA/Wealth executive role scoring engine  
✔ Balanced filtering (recall + precision)  

Target roles:
- Director of Operations
- Head of Operations
- Director of Service
- Head of Service
- VP Operations (Wealth / RIA)
- Client Service Leadership (Wealth)
""")

# ----------------------------
# 1. RIA / WEALTH ECOSYSTEM
# ----------------------------

RIA_COMPANIES = [
    "schwab",
    "fidelity",
    "lpl",
    "assetmark",
    "cetera",
    "kestra",
    "blackrock",
    "wealthfront",
    "betterment",
    "wealthsimple",
    "fisher",
    "morgan stanley wealth",
    "jpmorgan wealth",
    "ubs wealth",
    "raymond james"
]

# ----------------------------
# 2. ATS INGESTION LAYER
# ----------------------------

def fetch_greenhouse(company):
    jobs = []
    url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"

    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()

            for j in data.get("jobs", []):
                jobs.append({
                    "title": j.get("title", ""),
                    "company": company,
                    "link": j.get("absolute_url", ""),
                    "source": "greenhouse"
                })
    except:
        pass

    return jobs


def fetch_lever(company):
    jobs = []
    url = f"https://api.lever.co/v0/postings/{company}?mode=json"

    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()

            for j in data:
                jobs.append({
                    "title": j.get("text", ""),
                    "company": company,
                    "link": j.get("hostedUrl", ""),
                    "source": "lever"
                })
    except:
        pass

    return jobs


def fetch_all_jobs():
    all_jobs = []

    for c in RIA_COMPANIES:
        all_jobs.extend(fetch_greenhouse(c))
        all_jobs.extend(fetch_lever(c))

    return all_jobs

# ----------------------------
# 3. LINKEDIN DISCOVERY LAYER (NO SCRAPING)
# ----------------------------

def linkedin_search_urls():

    titles = [
        "Director of Operations",
        "Head of Operations",
        "Operations Director",
        "Director of Service",
        "Head of Service",
        "VP Operations",
        "VP Client Service",
        "Wealth Operations Director",
        "Client Service Director"
    ]

    firms = [
        "RIA",
        "wealth management",
        "registered investment advisor",
        "LPL Financial",
        "Charles Schwab Wealth",
        "Fidelity Wealth",
        "AssetMark",
        "Cetera",
        "Kestra",
        "Morgan Stanley Wealth",
        "JPMorgan Wealth Management"
    ]

    results = []

    for t in titles:
        for f in firms:

            query = f"{t} {f}"
            encoded = urllib.parse.quote(query)

            url = f"https://www.linkedin.com/jobs/search/?keywords={encoded}"

            results.append({
                "title": t,
                "company": f,
                "link": url,
                "source": "linkedin_search"
            })

    return results

# ----------------------------
# 4. COMBINED INGESTION
# ----------------------------

def fetch_all_sources():

    jobs = []

    # ATS
    for c in RIA_COMPANIES:
        jobs.extend(fetch_greenhouse(c))
        jobs.extend(fetch_lever(c))

    # LinkedIn discovery layer
    jobs.extend(linkedin_search_urls())

    return jobs

# ----------------------------
# 5. 🧠 BALANCED RIA ROLE SCORING ENGINE
# ----------------------------

def score_job(job):

    title = job["title"].lower()
    company = job["company"].lower()
    source = job["source"]

    text = title + " " + company

    score = 0

    # ----------------------------
    # HARD EXCLUSIONS (ONLY FOR ATS DATA)
    # ----------------------------
    if source != "linkedin_search":

        hard_block = [
            "engineer", "software", "ios", "android",
            "developer", "backend", "frontend",
            "marketing", "content", "copywriter",
            "legal", "counsel", "attorney",
            "hr", "recruiter",
            "payroll", "accounting", "tax", "audit",
            "teacher", "hospital", "chef",
            "mortgage", "loan", "lending",
            "bank branch", "retail banking"
        ]

        if any(x in text for x in hard_block):
            return -999

    # ----------------------------
    # COMPANY SIGNAL (STRONG WEIGHT)
    # ----------------------------
    if any(x in company for x in RIA_COMPANIES):
        score += 4

    # ----------------------------
    # ROLE INTENT SIGNALS
    # ----------------------------
    role_weights = {
        "director": 3,
        "head": 3,
        "vp": 3,
        "operations": 2,
        "service": 2,
        "client": 2,
        "advisor": 3,
        "wealth": 2,
        "trading": 2,
        "custody": 3,
        "clearing": 3,
        "portfolio": 2,
        "transition": 2,
        "onboarding": 2
    }

    for k, v in role_weights.items():
        if k in title:
            score += v

    return score

# ----------------------------
# 6. FILTER THRESHOLD
# ----------------------------

def is_relevant(job):
    return score_job(job) >= 6

# ----------------------------
# 7. LABELING
# ----------------------------

def label(score):
    if score >= 9:
        return "🔥 HIGH MATCH"
    elif score >= 7:
        return "⚡ STRONG MATCH"
    return "🟡 MODERATE"

def tier(title):

    t = title.lower()

    if "head" in t or "chief" in t:
        return "💰 $200k–$250k+"
    if "vp" in t:
        return "💰 $160k–$220k"
    if "director" in t:
        return "💰 $160k–$220k"
    return "💰 $140k–$170k"

def positioning(title):

    t = title.lower()

    if "vp" in t:
        return "Senior RIA ops leader bridging advisor experience and platform execution"
    if "director" in t:
        return "Operational leader owning advisor service delivery and scalability"
    if "head" in t:
        return "Enterprise operator shaping wealth operations strategy"
    return "RIA operations execution role"

# ----------------------------
# 8. EXECUTION
# ----------------------------

st.subheader("📡 Hybrid RIA + LinkedIn Intelligence Feed")

jobs = fetch_all_sources()

filtered = [j for j in jobs if is_relevant(j)]

scored = [(score_job(j), j) for j in filtered if score_job(j) != -999]
scored.sort(reverse=True, key=lambda x: x[0])

if not scored:
    st.warning("No matching RIA roles found (check thresholds or feed freshness).")

# ----------------------------
# 9. OUTPUT
# ----------------------------

for s, j in scored:

    st.markdown(f"### {j['title']}")
    st.write(f"🏢 {j['company']} ({j['source']})")
    st.write(f"🔗 {j['link']}")

    st.write(f"🎯 Score: {s}")
    st.write(label(s))
    st.write(tier(j["title"]))
    st.write(f"🧠 Positioning: {positioning(j['title'])}")

    st.divider()

# ----------------------------
# 10. SYSTEM STATE
# ----------------------------

st.subheader("⚡ System State")

st.write("""
✔ ATS ingestion active  
✔ LinkedIn discovery layer active (search-based)  
✔ Balanced scoring engine enabled  
✔ Hard exclusions applied to ATS only  
✔ RIA/Wealth executive role targeting enabled  
""")

st.success("RIA Hybrid Intelligence Engine v8 active: ATS + LinkedIn + scoring fusion live.")
