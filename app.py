import streamlit as st
import requests

st.title("🧠 RIA Executive Job OS (RIA-Only Intelligence Graph v3)")

st.write("""
This system is now strictly constrained to:

✔ RIA firms  
✔ Wealth management platforms  
✔ Advisory operations  
✔ Custody / clearing ecosystems  

It explicitly excludes:
✖ Banking operations  
✖ Mortgage / lending  
✖ Fraud / risk ops  
✖ Insurance  
✖ Engineering / IT roles (unless explicitly wealth-platform advisory systems)
""")

# ----------------------------
# 1. RIA FIRM DISCOVERY LAYER (CONSTRAINED CORE SET)
# ----------------------------

def discover_ria_firms():
    """
    This is intentionally constrained to known RIA / wealth ecosystem firms.
    No expansion into general financial services.
    """

    return [
        "wealthfront",
        "betterment",
        "fisherinvestments",
        "lpl",
        "schwab",
        "blackrock",
        "wealthsimple"
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
# 3. JOB INGESTION LAYER
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

    firms = discover_ria_firms()
    all_jobs = []

    for f in firms:
        all_jobs.extend(fetch_greenhouse(f))
        all_jobs.extend(fetch_lever(f))

    return all_jobs

# ----------------------------
# 5. STRICT RIA DOMAIN FILTER (CORE FIX)
# ----------------------------

def is_ria_relevant(title):

    t = title.lower()

    # -----------------------------
    # HARD EXCLUSIONS (STRICT)
    # -----------------------------
    exclude = [
        "mortgage",
        "loan",
        "lending",
        "fraud",
        "risk",
        "credit",
        "insurance",
        "banking",
        "branch",
        "call center",
        "retail",
        "underwriting",
        "engineering manager",
        "software engineer",
        "developer",
        "it support",
        "systems"
    ]

    if any(x in t for x in exclude):
        return False

    # -----------------------------
    # STRICT RIA / WEALTH SIGNALS
    # -----------------------------
    include = [
        "ria",
        "registered investment",
        "wealth management",
        "financial advisor",
        "advisor services",
        "investment advisory",
        "portfolio",
        "custody",
        "clearing",
        "trading",
        "client service",
        "wealth"
    ]

    return any(x in t for x in include)

# ----------------------------
# 6. SCORING ENGINE (POST-FILTER ONLY)
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

st.subheader("📡 RIA-Only Live Job Feed")

jobs = fetch_all_jobs()

# FILTER FIRST (CRITICAL CHANGE)
filtered = [j for j in jobs if is_ria_relevant(j["title"])]

if not filtered:
    st.warning("No RIA-relevant roles found in current ATS coverage.")

# ----------------------------
# 8. SCORE + SORT
# ----------------------------

scored = []

for j in filtered:
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
✔ RIA-only ingestion constraint active  
✔ Banking / mortgage / fraud / engineering excluded  
✔ Filter applied BEFORE scoring (critical fix)  
✔ ATS-based ingestion (Greenhouse + Lever only)  
""")

st.success("RIA Intelligence Graph v3 active: strict domain filtering + structured ingestion + ranking enabled.")
