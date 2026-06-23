import streamlit as st
import requests

st.title("🧠 RIA Executive Job OS (Intelligence Graph Mode)")

st.write("""
Live RIA job intelligence system with:

1. Discovery Layer (RIA/wealth firm expansion logic)
2. ATS Adapters (Greenhouse + Lever)
3. Normalization engine
4. Executive scoring + ranking system
""")

# ----------------------------
# 1. DISCOVERY LAYER (EXPANDABLE SEED GRAPH)
# ----------------------------

def discover_ria_firms():

    # NOTE: This is a seed graph (expandable over time)
    # In real systems, this would be fed by external discovery APIs

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
# 2. ATS DETECTION
# ----------------------------

def detect_ats(company):

    greenhouse = ["wealthfront", "betterment", "blackrock", "fisherinvestments"]
    lever = ["wealthsimple"]

    if company in greenhouse:
        return "greenhouse"
    if company in lever:
        return "lever"

    return "unknown"

# ----------------------------
# 3. JOB INGESTION LAYER (MULTI-ADAPTER)
# ----------------------------

def fetch_jobs_for_company(company):

    jobs = []
    ats = detect_ats(company)

    try:

        # ---------------- GREENHOUSE ----------------
        if ats == "greenhouse":
            url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
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

        # ---------------- LEVER ----------------
        elif ats == "lever":
            url = f"https://api.lever.co/v0/postings/{company}?mode=json"
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

# ----------------------------
# 4. FULL INGESTION PIPELINE
# ----------------------------

def fetch_all_jobs():

    firms = discover_ria_firms()
    all_jobs = []

    for f in firms:
        jobs = fetch_jobs_for_company(f)
        all_jobs.extend(jobs)

    return all_jobs

# ----------------------------
# 5. SCORING ENGINE (RIA EXECUTIVE MODEL)
# ----------------------------

def score(text):

    t = text.lower()
    s = 0

    # seniority
    if any(x in t for x in ["vp", "vice president"]):
        s += 3
    if any(x in t for x in ["director", "head"]):
        s += 3

    # operations core
    if "operations" in t:
        s += 2

    # wealth / ria relevance
    if any(x in t for x in ["wealth", "ria", "advisor", "client"]):
        s += 2

    # service layer
    if any(x in t for x in ["service", "experience"]):
        s += 1

    return s

def label(score):

    if score >= 6:
        return "🔥 HIGH CONVERSION (Apply Immediately)"
    if score >= 4:
        return "⚡ MEDIUM (Review Within 48h)"
    return "🟡 LOW (Optional)"

def comp_tier(text):

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
# 6. EXECUTION PIPELINE
# ----------------------------

st.subheader("📡 Live RIA Job Intelligence Feed")

jobs = fetch_all_jobs()

if not jobs:
    st.warning("No jobs returned. Some ATS systems may be unavailable or empty.")

scored = []

for job in jobs:
    s = score(job["title"])
    scored.append((s, job))

scored.sort(reverse=True, key=lambda x: x[0])

# ----------------------------
# 7. OUTPUT LAYER (RANKED FEED)
# ----------------------------

for s, job in scored:

    title = job["title"]

    st.markdown(f"### {title}")
    st.write(f"🏢 {job['company']} ({job['source']})")
    st.write(f"🔗 {job['link']}")

    st.write(comp_tier(title))
    st.write(f"🎯 Score: {s}/7")
    st.write(label(s))
    st.write(f"🧠 Positioning: {positioning(title)}")

    st.divider()

# ----------------------------
# 8. SYSTEM EXPLANATION
# ----------------------------

st.subheader("⚡ System Logic")

st.write("""
- Discovery Layer: identifies RIA/wealth firms (seed graph)
- ATS Layer: detects job board type (Greenhouse / Lever)
- Ingestion Layer: pulls structured job data
- Scoring Layer: ranks VP / Director / Ops relevance
- Output Layer: executive-ranked job feed
""")

st.success("RIA Intelligence Graph active: discovery + ingestion + scoring + ranking enabled.")
