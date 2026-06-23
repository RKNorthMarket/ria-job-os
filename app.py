import streamlit as st
from urllib.parse import quote

st.title("🧠 RIA Executive Job OS (Fit + Comp Tier Engine)")

st.write("""
Targeting RIAs ($500M+ AUM proxy) with automated compensation tier estimation.
""")

# ----------------------------
# ROLE QUERIES
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
# COMP TIER ENGINE (RULE-BASED)
# ----------------------------

def comp_tier(label: str):
    label_lower = label.lower()

    # Tier 3 (highest)
    if any(k in label_lower for k in ["head", "chief", "coo"]):
        return "💰 Tier 3 ($220k–$250k+ | Stretch / High Value)"

    if "vp" in label_lower:
        return "💰 Tier 2 ($160k–$220k | Target Zone)"

    if "director" in label_lower:
        return "💰 Tier 2 ($160k–$220k | Target Zone)"

    # fallback
    return "💰 Tier 1 ($140k–$160k | Baseline / Selective)"

# ----------------------------
# FIT MODEL (STATIC)
# ----------------------------

st.subheader("📊 Fit Model (Your Background Strengths)")

st.write("""
Scoring anchors:
- Goldman Sachs (Ops + scale)
- State Street (custody + servicing)
- BNY Mellon (client service leadership)
- RIA ecosystem exposure
- Platform transformation experience
""")

st.divider()

# ----------------------------
# JOB LINKS + TIERING
# ----------------------------

st.subheader("📌 RIA Job Search (500M+ Proxy Filter + Comp Tiers)")

for label, query in roles.items():

    url = f"https://www.google.com/search?q={quote(query + ' $500M AUM jobs')}"
    tier = comp_tier(label)

    st.markdown(f"### {label}")
    st.markdown(f"[View Jobs →]({url})")
    st.write(tier)

st.divider()

# ----------------------------
# EXECUTION GUIDANCE
# ----------------------------

st.subheader("⚡ Execution Rules")

st.write("""
Prioritization logic:

1. Tier 3 → Apply aggressively (high leverage roles)
2. Tier 2 → Primary target zone (core pipeline)
3. Tier 1 → Selective / fill-in opportunities

Focus on firms showing:
- multiple open ops roles
- recent postings
- platform or consolidation language
""")

st.success("Goal: maximize compensation + fit probability, not application volume.")
