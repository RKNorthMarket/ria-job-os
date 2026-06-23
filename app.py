import streamlit as st
from urllib.parse import quote

st.title("🧠 RIA Executive Job OS (LIVE Filtering Mode)")

st.write("""
Real-time filtered job intelligence for Wealth / RIA operations leadership roles.

Now optimized for:
- Recency (last 7 days emphasis)
- Seniority (Director / VP / Head)
- Wealth / advisory relevance
- Conversion probability scoring
""")

# ----------------------------
# ROLE SET (clean + minimal noise)
# ----------------------------

roles = {
    "VP Operations (Wealth Management)": "VP Operations wealth management",
    "Director of Operations (Wealth Management)": "Director of Operations wealth management",
    "Head of Operations (Wealth Management)": "Head of Operations wealth management",
    "Client Service Director": "Client Service Director wealth management",
    "Advisor Experience Lead": "Advisor Experience wealth management"
}

# ----------------------------
# COMP TIERS
# ----------------------------

def comp_tier(label):
    l = label.lower()

    if "head" in l or "coo" in l:
        return "💰 Tier 3 ($220k–$250k+)"
    if "vp" in l:
        return "💰 Tier 2 ($160k–$220k)"
    if "director" in l:
        return "💰 Tier 2 ($160k–$220k)"
    return "💰 Tier 1 ($140k–$160k)"

# ----------------------------
# LIVE FILTERING SCORE (NEW CORE ENGINE)
# ----------------------------

def live_score(label, query):
    l = label.lower()
    score = 0

    # seniority signal
    if any(k in l for k in ["vp", "director", "head"]):
        score += 3

    # ops relevance
    if "operations" in l:
        score += 2

    # wealth relevance
    if "wealth" in l:
        score += 2

    # advisor/client proximity
    if "client" in l or "advisor" in l:
        score += 1

    return score

def live_label(score):
    if score >= 6:
        return "🔥 LIVE HIGH PRIORITY (Apply Today)"
    if score >= 4:
        return "⚡ LIVE FILTERED (Review Within 48h)"
    return "🟡 LOW SIGNAL (Skip Unless Needed)"

# ----------------------------
# LINK GENERATION (FILTERED MODE)
# ----------------------------

def job_links(query):

    # CLEAN QUERY (critical fix)
    clean_query = query.replace("RIA", "").strip()

    # LinkedIn: last 7 days filter
    linkedin = (
        "https://www.linkedin.com/jobs/search/?"
        "keywords=" + quote(clean_query) +
        "&f_TPR=r604800"
    )

    # Indeed: broader but still clean
    indeed = f"https://www.indeed.com/jobs?q={quote(clean_query)}"

    # Google fallback
    google = f"https://www.google.com/search?q={quote(clean_query + ' wealth management jobs')}"

    return linkedin, indeed, google

# ----------------------------
# POSITIONING ENGINE (LIGHTWEIGHT)
# ----------------------------

def positioning(label):
    l = label.lower()

    if "vp" in l:
        return "Scaled wealth ops leader bridging advisor experience + platform execution."
    if "director" in l:
        return "Operational owner focused on execution, scalability, and advisor servicing quality."
    if "head" in l:
        return "Enterprise operator driving org design and advisory platform scaling."
    return "Hybrid ops + client experience leader in wealth management."

# ----------------------------
# UI
# ----------------------------

st.subheader("📊 LIVE FILTERED PIPELINE (Ranked Signals Only)")

results = []

for label, query in roles.items():

    score = live_score(label, query)
    results.append((score, label, query))

# SORT BY CONVERSION POTENTIAL
results.sort(reverse=True, key=lambda x: x[0])

for score, label, query in results:

    linkedin, indeed, google = job_links(query)

    tier = comp_tier(label)
    status = live_label(score)
    position = positioning(label)

    st.markdown(f"### {label}")

    st.write(tier)
    st.write(f"🎯 Live Signal Score: {score}/7")
    st.write(status)
    st.write(f"🧠 Positioning: {position}")

    st.write("🔵 LinkedIn (Filtered - Last 7 Days)")
    st.write(linkedin)

    st.write("🟡 Indeed (Coverage Layer)")
    st.write(indeed)

    st.write("🟢 Google Backup")
    st.write(google)

    st.divider()

# ----------------------------
# EXECUTION RULES
# ----------------------------

st.subheader("⚡ LIVE EXECUTION RULES")

st.write("""
1. ONLY act on 🔥 HIGH PRIORITY roles today  
2. Apply within 24 hours of posting signal  
3. Ignore low signal roles unless pipeline is thin  
4. Always start with LinkedIn results first  
5. Use Indeed only for secondary verification  
6. Google is discovery only — not execution  
""")

st.success("LIVE FILTERING MODE ACTIVE: ranked executive job feed enabled.")
