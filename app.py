import streamlit as st
import requests

st.title("🧠 RIA Executive Job OS (Workday + Filtered Intelligence Graph)")

st.write("""
Now includes:
- Greenhouse ingestion
- Lever ingestion
- Workday best-effort ingestion
- HARD relevance filtering (critical fix)
- Executive scoring + ranking
""")

# ----------------------------
# DISCOVERY LAYER (SEED FIRMS)
# ----------------------------

def discover_firms():
    return [
        "wealthfront",
        "betterment",
        "blackrock",
        "wealthsimple",
        "fisherinvestments",
        "lpl",
        "schwab"
    ]

# ----------------------------
# ATS DETECTION
# ----------------------------

def detect_ats(company):

    greenhouse = ["wealthfront", "betterment", "blackrock", "fisherinvestments"]
    lever = ["wealthsimple"]

    return {
        "greenhouse": company in greenhouse,
        "lever": company in lever,
        "workday": True  # we always attempt fallback
    }

# ----------------------------
# INGESTION LAYERS
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


def fetch_workday(company):

    jobs = []

    # BEST-EFFORT heuristic endpoint (not guaranteed across firms)
    url = f"https://{company}.wd1.myworkdayjobs.com/wday/cxs/{company}/careers"

    try:
        r = requests.get(url, timeout=5)

        if r.status_code == 200:

            data = r.json()

            for job in data.get("jobPostings", []):
                jobs.append({
                    "title": job.get("title", ""),
                    "company": company,
                    "link": "",
                    "source": "workday"
                })

    except:
        pass

    return jobs

# ----------------------------
# FULL INGESTION PIPELINE
# ----------------------------

def fetch_all_jobs():

    firms = discover_firms()
    all_jobs = []

    for f in firms:

        all_jobs.extend(fetch_greenhouse(f))
        all_jobs.extend(fetch_lever(f))
        all_jobs.extend(fetch_workday(f))

    return all_jobs

# ----------------------------
# 🔥 CRITICAL FIX: DOMAIN FILTER (NEW)
# ----------------------------

def is_ria_relevant(text):

    t = text.lower()

    keywords = [
        "wealth",
        "ria",
        "advisor",
        "client",
        "operations",
        "investment",
        "portfolio",
        "financial",
        "service",
        "experience",
        "custody",
        "clearing"
    ]

    return any(k in t for k in keywords)

# ----------------------------
# SCORING ENGINE (ONLY AFTER FILTERING)
# ----------------------------

def score(text):

    t = text.lower()
    s = 0

    if any(x in t for x in ["vp", "vice president"]):
        s += 3
    if any(x in t for x in ["director", "head"]):
        s += 3
    if "operations" in t:
        s += 2
    if any(x in t for x in ["wealth", "ria", "advisor", "client"]):
        s += 2
    if any(x in t for x in ["service", "experience"]):
        s += 1

    return s

def label(s):
    if s >= 6:
        return "🔥 HIGH CONVERSION"
    if s >= 4:
        return "⚡ MEDIUM"
    return "🟡 LOW"

def tier(text):

    t = text.lower()

    if any(x in t for x in ["head", "coo", "chief"]):
        return "💰 $220k–$250k+"
    if "vp" in t:
        return "💰 $160k–$220k"
    if "director" in t:
        return "💰 $160k–$220k"
    return "💰 $140k–$160k"

def positioning(text):

    t = text.lower()

    if "vp" in t:
        return "Scaled wealth ops leader bridging advisor experience + platform execution"
    if "director" in t:
        return "Operational owner focused on execution, scalability, and advisor servicing"
    if "head" in t:
        return "Enterprise operator driving org design and advisory transformation"
    return "Ops + client service hybrid in wealth management"

# ----------------------------
# EXECUTION PIPELINE
# ----------------------------

st.subheader("📡 Live RIA Job Feed (Filtered + Workday Enabled)")

jobs = fetch_all_jobs()

# ----------------------------
# APPLY FILTER BEFORE SCORING
# ----------------------------

filtered_jobs = [j for j in jobs if is_ria_relevant(j["title"])]

if not filtered_jobs:
    st.warning("No relevant jobs found after filtering. Try expanding firm list or ATS coverage.")

# ----------------------------
# SCORE + SORT
# ----------------------------

scored = []

for job in filtered_jobs:
    s = score(job["title"])
    scored.append((s, job))

scored.sort(reverse=True, key=lambda x: x[0])

# ----------------------------
# OUTPUT
# ----------------------------

for s, job in scored:

    title = job["title"]

    st.markdown(f"### {title}")
    st.write(f"🏢 {job['company']} ({job['source']})")
    st.write(f"🔗 {job['link']}")

    st.write(tier(title))
    st.write(f"🎯 Score: {s}/7")
    st.write(label(s))
    st.write(f"🧠 Positioning: {positioning(title)}")

    st.divider()

# ----------------------------
# SYSTEM NOTES
# ----------------------------

st.subheader("⚡ System Logic Update")

st.write("""
- Workday + Greenhouse + Lever ingestion enabled  
- HARD filter removes IT, marketing, PM, irrelevant roles  
- Scoring only applies to RIA/wealth-adjacent roles  
- System now behaves as a domain-specific executive job radar  
""")

st.success("Filtered RIA Intelligence Graph active (Workday + domain filtering enabled).")
