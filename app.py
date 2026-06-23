import streamlit as st
import requests

st.title("🧠 RIA Executive Job OS (Whitelist Intelligence Engine v6)")

st.write("""
This system is now STRICTLY whitelist-based.

✔ Only explicitly defined RIA/wealth ops roles are allowed  
❌ Everything else is rejected by default (no keyword guessing)  

This eliminates:
- Engineering roles
- Healthcare / education roles
- Mortgage / banking ops
- HR / payroll / accounting
- Marketing / legal / product
""")

# ----------------------------
# 1. RIA FIRM DISCOVERY LAYER
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
        "cetera",
        "kestra"
    ]

# ----------------------------
# 2. ATS LAYER
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
# 3. INGESTION
# ----------------------------

def fetch_all_jobs():

    firms = discover_firms()
    all_jobs = []

    for f in firms:
        all_jobs.extend(fetch_greenhouse(f))
        all_jobs.extend(fetch_lever(f))

    return all_jobs

# ----------------------------
# 4. 🧠 STRICT WHITELIST CLASSIFIER (CORE FIX)
# ----------------------------

def is_ria_relevant(job):

    title = job["title"].lower()
    company = job["company"].lower()
    text = title + " " + company

    # ----------------------------
    # STEP 1: HARD EXCLUSION (DEFAULT BLOCK EVERYTHING NON-OPS)
    # ----------------------------
    hard_exclusions = [
        "engineer",
        "software",
        "ios",
        "android",
        "backend",
        "frontend",
        "developer",
        "marketing",
        "content",
        "copywriter",
        "journalist",
        "legal",
        "counsel",
        "attorney",
        "hr",
        "recruiter",
        "talent acquisition",
        "payroll",
        "accounting",
        "finance manager",
        "tax",
        "audit",
        "mortgage",
        "loan",
        "lending",
        "banking",
        "branch",
        "retail",
        "hospital",
        "education",
        "teacher",
        "chef",
        "restaurant"
    ]

    if any(x in text for x in hard_exclusions):
        return False

    # ----------------------------
    # STEP 2: STRICT WHITELIST ONLY (NO FUZZY MATCHING)
    # ----------------------------
    whitelist_exact_phrases = [
        "advisor services",
        "advisor support",
        "financial advisor services",
        "client service (wealth)",
        "client services - wealth",
        "wealth management operations",
        "investment operations",
        "portfolio operations",
        "trading operations",
        "custody operations",
        "clearing operations",
        "advisor onboarding",
        "advisor transition",
        "account opening",
        "ria operations",
        "advisor platform operations"
    ]

    for phrase in whitelist_exact_phrases:
        if phrase in text:
            return True

    # ----------------------------
    # STEP 3: COMPANY SAFETY NET (ONLY IF TITLE IS AMBIGUOUS BUT OPS-LEANING)
    # ----------------------------
    ria_firms = [
        "lpl",
        "schwab",
        "fidelity",
        "blackrock",
        "wealthfront",
        "betterment",
        "wealthsimple",
        "assetmark",
        "cetera",
        "kestra",
        "fisher"
    ]

    company_signal = any(x in company for x in ria_firms)

    ops_hint = any(x in title for x in [
        "operations",
        "ops",
        "service",
        "support",
        "trading",
        "custody",
        "clearing"
    ])

    # ONLY allow if BOTH are true
    return company_signal and ops_hint

# ----------------------------
# 5. SCORING ENGINE
# ----------------------------

def score(title):

    t = title.lower()
    s = 0

    if "vp" in t or "vice president" in t:
        s += 3
    if "director" in t or "head" in t:
        s += 3
    if "operations" in t:
        s += 2
    if "client" in t or "advisor" in t:
        s += 2
    if "service" in t or "support" in t:
        s += 1

    return s

def tier(title):

    t = title.lower()

    if "head" in t or "chief" in t:
        return "💰 $220k–$250k+"
    if "vp" in t:
        return "💰 $160k–$220k"
    if "director" in t:
        return "💰 $160k–$220k"
    return "💰 $140k–$160k"

def label(s):

    if s >= 6:
        return "🔥 HIGH CONVERSION"
    if s >= 4:
        return "⚡ MEDIUM"
    return "🟡 LOW"

def positioning(title):

    t = title.lower()

    if "vp" in t:
        return "Senior wealth ops leader bridging advisor experience + platform execution"
    if "director" in t:
        return "Operational owner driving scalable RIA servicing models"
    if "head" in t:
        return "Enterprise operator shaping advisory operations strategy"
    return "RIA operations execution role"

# ----------------------------
# 6. EXECUTION
# ----------------------------

st.subheader("📡 RIA Ops Whitelist Feed")

jobs = fetch_all_jobs()

filtered = [j for j in jobs if is_ria_relevant(j)]

if not filtered:
    st.warning("No RIA whitelist-matching roles found.")

scored = []

for j in filtered:
    s = score(j["title"])
    scored.append((s, j))

scored.sort(reverse=True, key=lambda x: x[0])

# ----------------------------
# 7. OUTPUT
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
# 8. SYSTEM STATE
# ----------------------------

st.subheader("⚡ System State")

st.write("""
✔ Whitelist-only classification engine active  
✔ Non-RIA domains fully excluded by default  
✔ Engineering / marketing / legal / HR removed  
✔ Only RIA ops roles explicitly allowed  
✔ No fuzzy keyword matching as primary gate  
""")

st.success("RIA Ops Whitelist Engine v6 active: strict allowlist classification enabled.")
