import streamlit as st
import requests

st.title("🧠 RIA Executive Job OS (Discovery Layer + Live Feed Engine)")

st.write("""
This system now includes:

1. Discovery Layer (identifies relevant RIA / wealth firms)
2. Job Ingestion Layer (Greenhouse API)
3. Scoring Engine (VP / Director / Ops / Wealth relevance)
4. Ranked Executive Feed
""")

# ----------------------------
# 1. DISCOVERY LAYER (FIRM EXPANSION SEEDS)
# ----------------------------

DISCOVERY_FIRMS = [
    # Large RIAs / aggregators / wealth platforms
    "wealthfront",
    "betterment",
    "blackrock",
    "schwab",
    "lpl",
    "fidelity",

    # Mid-market RIAs / platforms (expandable ecosystem logic)
    "wealthsimple",
    "fisherinvestments",
]

st.subheader("🌐 Discovery Layer Active Firms")

st.write(", ".join(DISCOVERY_FIRMS))

# ----------------------------
# 2. JOB INGESTION (GREENHOUSE API)
# ----------------------------

def fetch_jobs():

    jobs = []

    for firm in DISCOVERY_FIRMS:

        try:
            url = f"https://boards-api.greenhouse.io/v1/boards/{firm}/jobs"
            r = requests.get(url, timeout=5)

            if r.status_code != 200:
                continue

            data = r.json()

            for job in data.get("jobs", []):

                jobs.append({
                    "title": job.get("title", ""),
                    "company": firm,
                    "link": job.get("absolute_url", ""),
                })

        except:
            continue

    return jobs

# ----------------------------
# 3. SCORING ENGINE
# ----------------------------

def score(text):
    t = text.lower()
    s = 0

    # seniority
    if any(x in t for x in ["vp", "vice president"]):
        s += 3
    if any(x in t for x in ["director", "head"]):
        s += 3

    # ops relevance
    if "operations" in t:
        s += 2

    # wealth / ria / advisor ecosystem
    if any(x in t for x in ["wealth", "ria", "advisor", "client"]):
        s += 2

    # service layer
    if any(x in t for x in ["service", "experience"]):
        s += 1

    return s

def label(s):
    if s >= 6:
        return "🔥 HIGH CONVERSION (Apply Immediately)"
    if s >= 4:
        return "⚡ MEDIUM (Review Within 48h)"
    return "🟡 LOW (Ignore Unless Needed)"

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
# 4. DATA PIPELINE
# ----------------------------

st.subheader("📡 Live Discovery + Job Feed")

jobs = fetch_jobs()

if not jobs:
    st.warning("No jobs returned. Some firms may block API access or have no active postings.")

# ----------------------------
# 5. RANKING
# ----------------------------

scored = []

for job in jobs:
    s = score(job["title"])
    scored.append((s, job))

scored.sort(reverse=True, key=lambda x: x[0])

# ----------------------------
# 6. OUTPUT
# ----------------------------

for s, job in scored:

    title = job["title"]

    st.markdown(f"### {title}")
    st.write(f"🏢 {job['company']}")
    st.write(f"🔗 {job['link']}")

    st.write(comp_tier(title))
    st.write(f"🎯 Score: {s}/7")
    st.write(label(s))
    st.write(f"🧠 Positioning: {positioning(title)}")

    st.divider()

# ----------------------------
# 7. SYSTEM LOGIC NOTES
# ----------------------------

st.subheader("⚡ System Behavior")

st.write("""
- Discovery Layer identifies firms in wealth/RIA ecosystem  
- Ingestion Layer pulls structured job data (Greenhouse API)  
- Scoring Layer ranks by executive relevance  
- Output = prioritized hiring pipeline  
""")

st.success("Discovery Layer Active: firm expansion + structured ingestion + ranked executive feed enabled.")
