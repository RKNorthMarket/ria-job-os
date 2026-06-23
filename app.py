import streamlit as st
import requests
import urllib.parse
from collections import defaultdict

st.title("🧠 RIA Executive Job OS (Personal Fit Engine v12 — Resume Calibrated)")

st.write("""
Now calibrated to YOUR background:

✔ RIA platform operations leadership ($350B AUM experience)  
✔ Wealth client service + advisor operations  
✔ Goldman Sachs + BNY Mellon + State Street experience  
✔ onboarding, KPI systems, service model transformation  
✔ enterprise operational risk + controls  

System now ranks jobs based on:
- Role alignment to your experience
- Platform + RIA ecosystem fit
- Seniority match (Director / VP / Head)
- Transformation + operations complexity
""")

# ----------------------------
# 1. RIA ECOSYSTEM
# ----------------------------

RIA_FIRMS = [
    "schwab", "fidelity", "lpl", "assetmark", "cetera",
    "kestra", "blackrock", "wealthfront", "betterment",
    "wealthsimple", "fisher",
    "morgan stanley wealth", "jpmorgan wealth",
    "ubs wealth", "raymond james"
]

# ----------------------------
# 2. ATS INGESTION
# ----------------------------

def fetch_greenhouse(company):
    jobs = []
    url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            for j in r.json().get("jobs", []):
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
            for j in r.json():
                jobs.append({
                    "title": j.get("text", ""),
                    "company": company,
                    "link": j.get("hostedUrl", ""),
                    "source": "lever"
                })
    except:
        pass
    return jobs


def fetch_ats():
    jobs = []
    for f in RIA_FIRMS:
        jobs.extend(fetch_greenhouse(f))
        jobs.extend(fetch_lever(f))
    return jobs

# ----------------------------
# 3. LINKEDIN LAYER
# ----------------------------

def linkedin_layer():

    titles = [
        "Director of Operations",
        "Head of Operations",
        "VP Operations",
        "Director of Service",
        "Head of Service"
    ]

    firms = [
        "RIA",
        "wealth management",
        "independent RIA",
        "family office",
        "Schwab Wealth",
        "Fidelity Wealth",
        "LPL Financial",
        "AssetMark",
        "Cetera"
    ]

    results = []

    for t in titles:
        for f in firms:
            q = urllib.parse.quote(f"{t} {f}")
            url = f"https://www.linkedin.com/jobs/search/?keywords={q}"

            results.append({
                "title": t,
                "company": f,
                "link": url,
                "source": "linkedin_search"
            })

    return results

# ----------------------------
# 4. INDEPENDENT RIA DISCOVERY
# ----------------------------

def independent_ria_layer():

    queries = [
        "independent RIA operations director hiring",
        "wealth advisory firm client service director jobs",
        "RIA firm head of operations hiring",
        "family office operations leadership jobs"
    ]

    results = []

    for q in queries:
        url = "https://www.google.com/search?q=" + urllib.parse.quote(q)

        results.append({
            "title": "Independent RIA Market Signal",
            "company": "independent RIA ecosystem",
            "link": url,
            "source": "market_discovery"
        })

    return results

# ----------------------------
# 5. MASTER PIPELINE
# ----------------------------

def fetch_all_sources():
    jobs = []
    jobs.extend(fetch_ats())
    jobs.extend(linkedin_layer())
    jobs.extend(independent_ria_layer())
    return jobs

# ----------------------------
# 6. 🧠 BASE ROLE SCORING (MARKET FIT)
# ----------------------------

def market_score(job):

    title = job["title"].lower()
    company = job["company"].lower()

    score = 0

    if any(x in company for x in RIA_FIRMS):
        score += 4

    signals = {
        "director": 3,
        "head": 3,
        "vp": 3,
        "operations": 2,
        "service": 2,
        "client": 2,
        "wealth": 2,
        "advisor": 3,
        "custody": 3,
        "clearing": 3,
        "onboarding": 2,
        "transition": 2
    }

    for k, v in signals.items():
        if k in title:
            score += v

    return score

# ----------------------------
# 7. 🧠 PERSONAL FIT ENGINE (RESUME CALIBRATED)
# ----------------------------

def fit_score(job):

    title = job["title"].lower()
    company = job["company"].lower()

    score = 0

    # ----------------------------
    # CORE EXPERIENCE ALIGNMENT
    # ----------------------------

    # RIA platform ops (State Street / Goldman / BNY alignment)
    if any(x in title for x in ["operations", "service", "client"]):
        score += 3

    # Strong match to your domain
    domain_strength = {
        "ria": 2,
        "wealth": 2,
        "advisor": 3,
        "custody": 3,
        "clearing": 3,
        "onboarding": 3,
        "transition": 2,
        "kpi": 2,
        "risk": 2,
        "controls": 2
    }

    for k, v in domain_strength.items():
        if k in title:
            score += v

    # ----------------------------
    # SENIORITY MATCH (YOUR LEVEL)
    # ----------------------------
    if "vp" in title:
        score += 5
    if "director" in title:
        score += 5
    if "head" in title:
        score += 6

    # ----------------------------
    # PLATFORM BONUS (HIGH FIT FOR YOUR EXPERIENCE)
    # ----------------------------
    if any(x in company for x in RIA_FIRMS):
        score += 3

    return score


def fit_label(score):

    if score >= 14:
        return "🔥 EXCELLENT FIT (HIGH PRIORITY APPLY)"
    if score >= 11:
        return "⚡ STRONG FIT (PRIORITY TARGET)"
    if score >= 8:
        return "🟡 MODERATE FIT"
    return "🔵 LOW FIT"

# ----------------------------
# 8. EXECUTION
# ----------------------------

st.subheader("📡 RIA Executive Fit Engine (Resume-Calibrated)")

jobs = fetch_all_sources()

ranked = []

for j in jobs:

    m = market_score(j)
    f = fit_score(j)
    total = m + f

    if total >= 11:
        ranked.append((total, m, f, j))

ranked.sort(reverse=True, key=lambda x: x[0])

# ----------------------------
# 9. OUTPUT
# ----------------------------

st.subheader("🎯 Ranked Roles (Personal Fit + Market Score)")

for total, m, f, j in ranked:

    st.markdown(f"### {j['title']}")
    st.write(f"🏢 {j['company']} ({j['source']})")
    st.write(f"🔗 {j['link']}")

    st.write(f"📊 Market Score: {m}")
    st.write(f"🧠 Fit Score: {f}")
    st.write(f"⭐ Total Score: {total}")
    st.write(f"🎯 Fit Rating: {fit_label(f)}")

    st.divider()

# ----------------------------
# 10. SYSTEM STATE
# ----------------------------

st.subheader("⚡ System State")

st.write("""
✔ Resume-calibrated fit engine active  
✔ RIA platform bias aligned to your experience  
✔ VP/Director/Head weighting optimized  
✔ Client service + onboarding + ops transformation prioritized  
✔ Market + personal fit hybrid scoring enabled  
""")

st.success("RIA Personal Fit Engine v12 active: calibrated to your executive experience profile.")
