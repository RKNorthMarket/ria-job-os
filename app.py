import streamlit as st

st.title("🧠 RIA Executive Job OS (Role Scoring Overlay Mode)")

st.write("""
This mode is designed to fix noisy job feeds (LinkedIn / Indeed).

Instead of relying on platform filtering:
👉 YOU paste roles
👉 The system scores them instantly
""")

# ----------------------------
# COMP TIERS
# ----------------------------

def comp_tier(text):
    t = text.lower()

    if any(k in t for k in ["head", "coo", "chief"]):
        return "💰 Tier 3 ($220k–$250k+)"
    if "vp" in t:
        return "💰 Tier 2 ($160k–$220k)"
    if "director" in t:
        return "💰 Tier 2 ($160k–$220k)"
    return "💰 Tier 1 ($140k–$160k)"

# ----------------------------
# ROLE SCORING ENGINE (CORE)
# ----------------------------

def score_role(text):
    t = text.lower()
    score = 0

    # seniority
    if any(k in t for k in ["vp", "director", "head", "chief"]):
        score += 3

    # ops relevance
    if "operations" in t:
        score += 2

    # wealth / ria relevance
    if any(k in t for k in ["wealth", "ria", "advisor"]):
        score += 2

    # client/service adjacency
    if any(k in t for k in ["client", "service"]):
        score += 1

    return score

def label(score):
    if score >= 6:
        return "🔥 HIGH CONVERSION (Apply / Engage Immediately)"
    if score >= 4:
        return "⚡ MEDIUM CONVERSION (Review Within 48h)"
    return "🟡 LOW CONVERSION (Usually Ignore)"

def positioning(text):
    t = text.lower()

    if "vp" in t:
        return "Scaled wealth ops leader bridging advisor experience + platform execution"
    if "director" in t:
        return "Operational owner focused on execution, scalability, and service quality"
    if "head" in t:
        return "Enterprise operator driving org design and advisory platform scaling"
    return "Ops + client experience hybrid in wealth management environments"

# ----------------------------
# INPUT LAYER (NEW CORE)
# ----------------------------

st.subheader("📥 Paste Job Titles Here (from LinkedIn / Indeed / anywhere)")

jobs_input = st.text_area(
    "Enter one job per line:",
    height=200,
    placeholder="""
VP Operations - Wealth Management Firm
Director of Operations - RIA Advisory Firm
Client Service Associate - Bank Branch
Head of Advisor Experience - Wealth Platform
Operations Manager - Insurance Company
"""
)

# ----------------------------
# PROCESSING
# ----------------------------

if jobs_input:

    jobs = [j.strip() for j in jobs_input.split("\n") if j.strip()]

    results = []

    for job in jobs:
        s = score_role(job)
        results.append((s, job))

    # sort high → low
    results.sort(reverse=True, key=lambda x: x[0])

    st.subheader("📊 Scored Pipeline (Ranked)")

    for score, job in results:

        tier = comp_tier(job)
        tag = label(score)
        pos = positioning(job)

        st.markdown(f"### {job}")
        st.write(tier)
        st.write(f"🎯 Score: {score}/7")
        st.write(tag)
        st.write(f"🧠 Positioning: {pos}")
        st.divider()

# ----------------------------
# GUIDANCE
# ----------------------------

st.subheader("⚡ How to Use This")

st.write("""
1. Open LinkedIn / Indeed normally  
2. Ignore sorting entirely  
3. Copy job titles you see  
4. Paste them here  
5. Let the system rank them  
""")

st.success("Role Scoring Overlay Active: OS now replaces platform filtering.")
