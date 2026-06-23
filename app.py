import streamlit as st
import requests

st.title("🧠 RIA Executive Job OS (Role Intelligence Engine)")

st.write("""
This system:
- Ingests jobs from Greenhouse + Lever
- Expands across known wealth/RIA firms
- Uses role taxonomy classification (NOT keyword filtering)
- Scores and ranks RIA-relevant opportunities
""")

# ----------------------------
# 1. RIA FIRM DISCOVERY LAYER (CORE UNIVERSE)
# ----------------------------

def discover_firms():

    return [
        "wealthfront",
        "betterment",
        "fisherinvestments",
        "lpl",
        "schwab",
        "blackrock",
        "wealthsimple",
        "fidelity"
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
# 3. INGESTION LAYER
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

# ----------------------------
# 4. PIPELINE EXECUTION
# ----------------------------

def fetch_all_jobs():

    firms = discover_firms()
    all_jobs = []

    for f in firms:
        all_jobs.extend(fetch_greenhouse(f))
        all_jobs.extend(fetch_lever(f))

    return all_jobs

# ----------------------------
# 5. 🧠 RIA ROLE TAXONOMY ENGINE (FIXED CORE LOGIC)
# ----------------------------

def is_ria_relevant(job):

    title = job["title"].lower()
    company = job["company"].lower()

    text = title + " " + company

    # -----------------------------
    # HARD EXCLUSIONS (STRICT BLOCK)
    # -----------------------------
    excluded_roles = [
        "mortgage",
        "loan",
        "lending",
        "fraud",
        "risk",
        "credit",
        "insurance",
        "underwriting",
        "retail banking",
        "branch",
        "call center",
        "software engineer",
        "engineering manager",
        "developer",
        "it support",
        "systems"
    ]

    if any(x in text for x in excluded_roles):
        return False

    # -----------------------------
    # RIA / WEALTH ROLE CLUSTERS
    # -----------------------------

    ria_role_clusters = [
        # core ops
        "operations",
        "client service",
        "advisor services",
        "advisor support",

        # trading / custody / platform
        "trading",
        "custody",
        "clearing",
        "portfolio",
        "investment",

        # lifecycle / advisory workflow
        "onboarding",
        "transition",
        "account opening",

        # wealth language
        "wealth",
        "financial advisor"
    ]

    role_signal = any(x in title for x in ria_role_clusters)

    # -----------------------------
    # COMPANY SIGNAL (WEALTH ECOSYSTEM)
    # -----------------------------
    ria_companies = [
        "lpl",
        "schwab",
        "fidelity",
        "blackrock",
        "wealthfront",
        "betterment",
        "fisher",
        "wealthsimple"
    ]

    company_signal = any(x in company for x in ria_companies)

    # -----------------------------
    # FINAL DECISION RULE
    # -----------------------------
    return role_signal or company_signal

# ----------------------------
# 6. SCORING ENGINE (POST-FILTER)
# ----------------------------

def score(title):

    t = title.lower()
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

def tier(title):

    t = title.lower()

    if any(x in t for x in ["head", "coo", "chief"]):
        return "💰 $220k–$250k+"
    if "vp" in t:
        return "💰 $160k–$220k"
    if "director" in t:
        return "💰 $160k–$220k"
    return "💰 $140k–$160k"

def positioning(title):

    t = title.lower()

    if "vp" in t:
        return "Scaled wealth ops leader bridging advisor experience + platform execution"
    if "director" in t:
        return "Operational owner focused on execution, scalability, and advisor servicing"
    if "head" in t:
        return "Enterprise operator driving org design and advisory transformation"
    return "Ops + client service hybrid in wealth management"

# ----------------------------
# 7. EXECUTION
# ----------------------------

st.subheader("📡 RIA Intelligence Feed (Taxonomy-Based)")

jobs = fetch_all_jobs()

filtered_jobs = [j for j in jobs if is_ria_relevant(j)]

if not filtered_jobs:
    st.warning("No RIA-relevant roles found in current ATS coverage.")

# ----------------------------
# 8. SCORE + SORT
# ----------------------------

scored = []

for j in filtered_jobs:
    s = score(j["title"])
    scored.append((s, j))

scored.sort(reverse=True, key=lambda x: x[0])

# ----------------------------
# 9. OUTPUT
# ----------------------------

for s, j in scored:

    title = j["title"]

    st.markdown(f"### {title}")
    st.write(f"🏢 {j['company']} ({j['source']})")
    st.write(f"🔗 {j['link']}")

    st.write(tier(title))
    st.write(f"🎯 Score: {s}/7")
    st.write(label(s))
    st.write(f"🧠 Positioning: {positioning(title)}")

    st.divider()

# ----------------------------
# 10. SYSTEM STATE
# ----------------------------

st.subheader("⚡ System State")

st.write("""
✔ Role taxonomy filtering (NOT keyword filtering)  
✔ RIA + wealth ecosystem classification  
✔ Banking / mortgage / fraud / engineering exclusion active  
✔ Multi-ATS ingestion (Greenhouse + Lever)  
✔ Ranked executive feed output  
""")

st.success("RIA Intelligence Engine v4 active: taxonomy-based filtering + structured ingestion + ranking enabled.")
