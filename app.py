import streamlit as st
from urllib.parse import quote

st.title("🧠 RIA Executive Job OS (Pipeline Control + Conversion Engine)")

st.write("""
Hybrid job launcher optimized for wealth management / RIA operations leadership roles.
Focus: Director, VP, Head of Operations, Client Service leadership.
""")

# ----------------------------
# ROLE QUERIES (cleaned inputs)
# ----------------------------

roles = {
    "Director of Operations (Wealth Management)": "Director of Operations wealth management",
    "VP Operations (Wealth Management)": "VP Operations wealth management",
    "Head of Operations (Wealth Management)": "Head of Operations wealth management",
    "Client Service Director": "Client Service Director wealth management",
    "Advisor Experience Leader": "Advisor Experience wealth management",
    "Practice Management Lead": "Practice Management wealth management"
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
# CONVERSION SCORE ENGINE
# ----------------------------

def conversion_score(label):
    l = label.lower()
    score = 0

    if any(k in l for k in ["director", "vp", "head"]):
        score += 3
    if "operations" in l:
        score += 2
    if "wealth" in l:
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
# HYBRID JOB LINKS (FIXED)
# ----------------------------

def job_links(query):

    clean_query = query.replace("RIA", "").strip()

    # LinkedIn FIX: structured + last 7 days filter
    linkedin = (
        "https://www.linkedin.com/jobs/search/?"
        "keywords=" + quote(clean_query) +
        "&f_TPR=r604800"
    )

    # Indeed fallback
    indeed = f"https://www.indeed.com/jobs?q={quote(clean_query)}"

    # Google backup
    google = f"https://www.google.com/search?q={quote(query + ' jobs')}"

    return linkedin, indeed, google

# ----------------------------
# POSITIONING ENGINE (LIGHTWEIGHT BUT INTENTIONAL)
# ----------------------------

def positioning(label):
    l = label.lower()

    if "vp" in l:
        return "Scaled ops leader bridging advisor experience + platform operations in wealth environments."
    if "director" in l:
        return "Operational owner focused on execution, scalability, and advisor/client service quality."
    if "head" in l or "coo" in l:
        return "Enterprise operator driving org design, scaling, and advisory platform transformation."
    return "Hybrid operations + client experience leader in wealth management environments."

# ----------------------------
# UI
# ----------------------------

st.subheader("📊 Hybrid Pipeline Control (Fixed LinkedIn + Real Jobs)")

for label, query in roles.items():

    linkedin, indeed, google = job_links(query)

    tier = comp_tier(label)
    conv = conversion_score(label)
    conv_label = conversion_label(conv)
    position = positioning(label)

    st.markdown(f"### {label}")

    st.write(tier)
    st.write(f"🎯 Conversion Score: {conv}/7")
    st.write(conv_label)
    st.write(f"🧠 Positioning: {position}")

    st.write("🔵 LinkedIn Jobs")
    st.write(linkedin)

    st.write("🟡 Indeed Jobs")
    st.write(indeed)

    st.write("🟢 Google Backup")
    st.write(google)

    st.divider()

# ----------------------------
# EXECUTION RULES
# ----------------------------

st.subheader("⚡ Execution Rules")

st.write("""
1. Start with 🔥 HIGH CONVERSION roles  
2. Use LinkedIn first (recent postings only)  
3. Use Indeed for coverage gaps  
4. Use Google only for discovery fallback  
5. Ignore low signal results — refine by firm, not keyword noise  
""")

st.success("System stabilized: LinkedIn filtering corrected + job signal quality improved.")
