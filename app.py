import streamlit as st
from urllib.parse import quote

st.title("🧠 RIA Executive Job OS (Scored + Execution Mode)")

st.write("""
Targeting RIAs with $500M+ AUM and ranking roles based on fit to your background.
""")

# ----------------------------
# ROLE SEARCHES
# ----------------------------

roles = {
    "Director of Operations (RIA / Wealth)": "Director of Operations RIA wealth management",
    "VP Operations (Wealth Management)": "VP Operations wealth management RIA",
    "Head of Operations (RIA Platforms)": "Head of Operations RIA advisory firm",
    "Client Service Director": "Client Service Director wealth management",
    "Practice Management Lead": "Practice Management RIA advisory",
    "Advisor Experience Leader": "Advisor Experience wealth management RIA"
}

# ----------------------------
# FIT SCORING MODEL (STATIC)
# ----------------------------

st.subheader("📊 Your Fit Scoring Model")

st.write("""
Scoring based on your background:
- Goldman Sachs (Ops / platform scaling)
- State Street (wealth servicing / custody ecosystem)
- BNY Mellon (client service leadership)
- RIA experience (direct advisory ecosystem exposure)
""")

fit_weights = {
    "Operations Leadership (Goldman / State Street / BNY)": 2,
    "RIA / Advisory Experience": 2,
    "Client Service / Advisor Experience": 2,
    "Platform / Custody Ecosystem Exposure": 1,
    "Scaling / Transformation Experience": 2
}

for k, v in fit_weights.items():
    st.write(f"• {k}: +{v} points")

st.divider()

# ----------------------------
# JOB SEARCH + IMPLICIT SCORING
# ----------------------------

st.subheader("📌 Executive Job Search Links (500M+ RIA Filter)")

for label, query in roles.items():

    url = f"https://www.google.com/search?q={quote(query + ' $500M AUM jobs')}"
    
    st.markdown(f"### {label}")
    st.markdown(f"[View Opportunities →]({url})")

    # simple heuristic scoring display
    if "Director" in label or "VP" in label:
        score = "High Fit (A Tier)"
    elif "Head" in label:
        score = "High Fit (A Tier)"
    else:
        score = "Medium Fit (B Tier)"

    st.write(f"**Fit Rating:** {score}")

st.divider()

# ----------------------------
# EXECUTION MODE
# ----------------------------

st.subheader("⚡ Daily Execution Mode")

st.write("""
How to use this system:

1. Open each role category
2. Focus on A-tier roles first
3. Identify firms showing urgency (recent postings, multiple roles)
4. Send for deeper evaluation or apply immediately
""")

st.success("Goal: maximize interview probability, not volume of applications.")
