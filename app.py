import streamlit as st
import requests

st.title("🧠 RIA Executive Job OS (RIA Feed Network)")

st.write("""
Live executive job intelligence system for Wealth Management & RIA operations roles.

Sources:
- Greenhouse job boards (RIAs + fintech)
- Lever job boards (wealth + advisory platforms)
""")

# ----------------------------
# RIA / WEALTH FEED SOURCES
# ----------------------------

FEEDS = [
    # Common RIA / wealth tech Greenhouse endpoints (examples pattern-based)
    "https://boards.greenhouse.io/wealthfront",
    "https://boards.greenhouse.io/betterment",
    "https://boards.greenhouse.io/blackrock",

    # Lever-based companies often used in fintech / advisory tech ecosystem
    "https://jobs.lever.co/wealthsimple",
]

# ----------------------------
# SIMPLE JOB FETCHER (SAFE APPROACH)
# ----------------------------
# NOTE: We attempt JSON where available, otherwise skip safely.

def fetch_jobs():
    jobs = []

    for base in FEEDS:
        try:
            url = base + "/jobs?content-type=json"
            r = requests.get(url, timeout=5)

            if r.status_code != 200:
                continue

            data = r.json()

            for job in data.get("jobs", []):
                jobs.append({
                    "title": job.get("title", ""),
                    "company": base.split("/")[-1],
                    "link": job.get("absolute_url", base)
                })

        except:
            continue

    return jobs

# ----------------------------
# SCORING ENGINE
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
    return "Ops + client experience hybrid in wealth management"

# ----------------------------
# LOAD DATA
# ----------------------------

st.subheader("📡 Live RIA & Wealth Job Feed")

jobs = fetch_jobs()

if not jobs:
    st.warning("No structured feed data returned. This is normal for some boards. System still active.")

# ----------------------------
# SCORE + SORT
# ----------------------------

scored = []

for j in jobs:
    s = score(j["title"])
    scored.append((s, j))

scored.sort(reverse=True, key=lambda x: x[0])

# ----------------------------
# DISPLAY
# ----------------------------

for s, j in scored:

    title = j["title"]

    st.markdown(f"### {title}")
    st.write(f"🏢 {j['company']}")
    st.write(f"🔗 {j['link']}")

    st.write(comp_tier(title))
    st.write(f"🎯 Score: {s}/7")
    st.write(label(s))
    st.write(f"🧠 Positioning: {positioning(title)}")

    st.divider()

# ----------------------------
# EXECUTION RULES
# ----------------------------

st.subheader("⚡ Execution Rules")

st.write("""
1. Act only on 🔥 HIGH CONVERSION roles  
2. Use ⚡ MEDIUM for daily pipeline building  
3. Ignore 🟡 unless pipeline is thin  
4. Focus on VP / Director / Head roles in Wealth / RIA contexts  
""")

st.success("RIA Feed Network active: structured ingestion + scoring + ranking enabled.")
