import streamlit as st
from urllib.parse import quote

st.title("🧠 RIA Executive Job OS (Hybrid Job Launcher)")

st.write("""
Targeting RIAs ($500M+ proxy) with multi-source job discovery:
- LinkedIn Jobs (primary)
- Indeed Jobs (secondary)
- Google fallback (broad discovery)
""")

# ----------------------------
# ROLE QUERIES
# ----------------------------

roles = {
    "Director of Operations (RIA / Wealth)": "Director of Operations RIA wealth management",
    "VP Operations (Wealth Management)": "VP Operations wealth management RIA",
    "Head of Operations (RIA Platforms)": "Head of Operations RIA advisory firm",
    "Client Service Director": "Client Service Director wealth management",
    "Advisor Experience Leader": "Advisor Experience RIA wealth management",
    "Practice Management Lead": "Practice Management RIA advisory"
}

# ----------------------------
# COMP TIERS
# ----------------------------

def comp_tier(label):
    l = label.lower()

    if any(k in l for k in ["head", "chief", "coo"]):
        return "💰 Tier 3 ($220k–$250k+)"
    if "vp" in l:
        return "💰 Tier 2 ($160k–$220k)"
    if "director" in l:
        return "💰 Tier 2 ($160k–$220k)"
    return "💰 Tier 1 ($140k–$160k)"

# ----------------------------
# CONVERSION SCORE
# ----------------------------

def conversion_score(label):
    l = label.lower()
    score = 0

    if any(k in l for k in ["director", "vp", "head"]):
        score += 3
    if "operations" in l:
        score += 2
    if "ria" in l or "wealth" in l:
        score += 2
    if "client" in l or "advisor" in l:
        score += 1

    return score

def conversion_label(score):
    if score >= 6:
        return "🔥 HIGH CONVERSION"
    if score >= 4:
        return "⚡ MEDIUM CONVERSION"
    return "🟡 LOW CONVERSION"

# ----------------------------
# HYBRID JOB LAUNCHER (NEW CORE FIX)
# ----------------------------

def job_links(query):
    q = quote(query + " jobs")

    linkedin = f"https://www.linkedin.com/jobs/search/?keywords={quote(query)}"
    indeed = f"https://www.indeed.com/jobs?q={quote(query)}"
    google = f"https://www.google.com/search?q={q}"

    return linkedin, indeed, google

# ----------------------------
# UI
# ----------------------------

st.subheader("📊 Hybrid Job Launcher (Real Job Sources)")

for label, query in roles.items():

    linkedin, indeed, google = job_links(query)

    tier = comp_tier(label)
    conv = conversion_score(label)
    conv_label = conversion_label(conv)

    st.markdown(f"### {label}")

    st.write(tier)
    st.write(f"🎯 Conversion Score: {conv}/7")
    st.write(conv_label)

    st.write("🔵 [LinkedIn Jobs](" + linkedin + ")")
    st.write("🟡 [Indeed Jobs](" + indeed + ")")
    st.write("🟢 [Google Search](" + google + ")")

    st.divider()

# ----------------------------
# EXECUTION RULES
# ----------------------------

st.subheader("⚡ Execution Rules")

st.write("""
1. Start with 🔥 HIGH CONVERSION roles  
2. Use LinkedIn first (highest signal for RIAs)  
3. Use Indeed to catch smaller RIAs not on LinkedIn  
4. Use Google only for backup discovery  
""")

st.success("System upgraded: direct job discovery enabled across multiple sources.")
