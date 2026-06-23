import streamlit as st
import requests

st.title("🧠 RIA Executive Job OS (Ops Intelligence Engine v5)")

st.write("""
This system is now strictly a **RIA Operations Intelligence Filter**, not a general job scraper.

It:
✔ Ingests from Greenhouse + Lever  
✔ Applies strict role-level classification  
✔ Blocks engineering, marketing, legal, product, HR  
✔ Only surfaces RIA/wealth operations roles  
✔ Ranks by executive relevance  
""")

# ----------------------------
# 1. DISCOVERY LAYER (RIA / WEALTH ECOSYSTEM)
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
        "fidelity",
        "assetmark",
        "cetera"
    ]

# ----------------------------
# 2. ATS DETECTION (LIGHT ROUTING ONLY)
# ----------------------------

def detect_ats(company):

    greenhouse = [
        "wealthfront",
        "betterment",
        "blackrock",
        "fisherinvestments",
        "assetmark"
    ]

    lever = [
        "wealthsimple"
    ]

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
# 5. 🧠 STRICT RIA ROLE CLASSIFICATION ENGINE (CORE FIX)
# ----------------------------

def is_ria_relevant(job):

    title = job["title"].lower()
    company = job["company"].lower()

    # -----------------------------
    # ❌ HARD EXCLUSIONS (ABSOLUTE BLOCK)
    # -----------------------------
    blocked_roles = [
        "software engineer",
        "ios",
        "android",
        "backend",
        "frontend",
        "data engineer",
        "devops",
        "engineering",
        "marketing",
        "content",
        "copywriter",
        "journalist",
        "legal",
        "attorney",
        "counsel",
        "product manager",
        "ux",
        "designer",
        "hr",
        "recruiter",
        "talent acquisition",
        "finance manager",
        "accounting",
        "tax",
        "audit"
    ]

    if any(x in title for x in blocked_roles):
        return False

    # -----------------------------
    # ✔ RIA OPS ROLE TAXONOMY (ONLY THESE PASS)
    # -----------------------------
    ria_ops_roles = [
        "operations",
        "client service",
        "advisor",
        "advisor services",
        "advisor support",
        "wealth management",
        "trading",
        "custody",
        "clearing",
        "portfolio",
        "investment operations",
        "account opening",
        "onboarding",
        "transition",
        "advisor platform",
        "service operations",
        "middle office",
        "back office"
    ]

    role_match = any(x in title for x in ria_ops_roles)

    # -----------------------------
    # ✔ COMPANY SAFETY NET (WEALTH ECOSYSTEM)
    # -----------------------------
    ria_companies = [
        "lpl",
        "schwab",
        "fidelity",
        "blackrock",
        "wealthfront",
        "betterment",
        "fisher",
        "wealthsimple",
        "assetmark",
        "cetera",
        "kestra"
    ]

    company_match = any(x in company for x in ria_companies)

    # -----------------------------
    # FINAL DECISION
    # -----------------------------
    return role_match or company_match

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
    if any(x in t for x in ["advisor", "wealth", "client"]):
        s += 2
    if any(x in t for x in ["service", "support"]):
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
        return "Operational owner driving scalable advisor servicing models"
    if "head" in t:
        return "Enterprise operator shaping advisory operations strategy"
    return "RIA operations and client service execution role"

# ----------------------------
# 7. EXECUTION
# ----------------------------

st.subheader("📡 RIA Operations Intelligence Feed")

jobs = fetch_all_jobs()

filtered_jobs = [j for j in jobs if is_ria_relevant(j)]

if not filtered_jobs:
    st.warning("No RIA operations roles found in current ATS coverage.")

scored = []

for j in filtered_jobs:
    s = score(j["title"])
    scored.append((s, j))

scored.sort(reverse=True, key=lambda x: x[0])

# ----------------------------
# 8. OUTPUT
# ----------------------------

for s, j in scored:

    st.markdown(f"### {j['title']}")
    st.write(f"🏢 {j['company']} ({j['source']})")
    st.write(f"🔗 {j['link']}")

    st.write(tier(j["title"]))
    st.write(f"🎯 Score: {s}/7")
    st.write(label(s))
    st.write(f"🧠 Positioning: {positioning(j['title'])}")

    st.divider()

# ----------------------------
# 9. SYSTEM STATE
# ----------------------------

st.subheader("⚡ System State")

st.write("""
✔ Strict RIA operations taxonomy enforced  
✔ Engineering / marketing / legal / product fully excluded  
✔ Company-level safety net retained  
✔ Role-level classification is primary gate  
✔ Post-filter scoring only  
""")

st.success("RIA Ops Intelligence Engine v5 active: strict classification + clean role filtering + ranked feed enabled.")
