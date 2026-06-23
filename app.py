import streamlit as st
from urllib.parse import quote

st.title("🧠 RIA Executive Job OS (Decision Layer Engine)")

st.write("""
RIAs ($500M+ proxy filter) + Executive prioritization engine.
This system helps you decide what to pursue, not just what exists.
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
# COMP TIERS (UNCHANGED)
# ----------------------------

def comp_tier(label: str):
    l = label.lower()

    if any(k in l for k in ["head", "chief", "coo"]):
        return "💰 Tier 3 ($220k–$250k+ | Stretch / High Value)"

    if "vp" in l:
        return "💰 Tier 2 ($160k–$220k | Target Zone)"

    if "director" in l:
        return "💰 Tier 2 ($160k–$220k | Target Zone)"

    return "💰 Tier 1 ($140k–$160k | Baseline / Selective)"

# ----------------------------
# FIT SCORE ENGINE (NEW)
# ----------------------------

def fit_score(label: str):
    score = 0

    l = label.lower()

    # your background alignment
    score += 2  # ops leadership baseline always relevant

    if "director" in l or "vp" in l or "head" in l:
        score += 3

    if "operations" in l:
        score += 2

    if "client service" in l or "advisor experience" in l:
        score += 2

    # scale inference bonus
    if "ria" in l:
        score += 2

    return score

def decision_label(score):
    if score >= 7:
        return "🔥 PRIORITY (High Probability)"
    if score >= 5:
        return "⚡ TARGET (Strong Fit)"
    return "🟡 SELECTIVE (Review Only)"

# ----------------------------
# UI
# ----------------------------

st.subheader("📊 Executive Decision Layer Output")

st.divider()

for label, query in roles.items():

    url = f"https://www.google.com/search?q={quote(query + ' $500M AUM jobs')}"

    tier = comp_tier(label)
    score = fit_score(label)
    decision = decision_label(score)

    st.markdown(f"### {label}")
    st.markdown(f"[View Jobs →]({url})")

    st.write(tier)
    st.write(f"🎯 Fit Score: {score} / 10")
    st.write(f"📌 Decision: {decision}")

st.divider()

st.subheader("⚡ How to Use This System")

st.write("""
1. Start with 🔥 PRIORITY roles  
2. Then ⚡ TARGET roles  
3. Ignore 🟡 SELECTIVE unless pipeline is thin  

Goal: maximize interview probability per hour invested.
""")

st.success("This is now a decision engine, not a job board.")
st.divider()

st.subheader("📬 Executive Daily Brief (Priority View)")

priority_roles = [
    "Director of Operations (RIA / Wealth)",
    "VP Operations (Wealth Management)",
    "Head of Operations (RIA Platforms)"
]

st.write("Top focus areas today:")

for r in priority_roles:
    st.write(f"🔥 {r}")

st.write("""
### Execution Rule:
- Spend 70% of time on 🔥 PRIORITY roles
- 25% on ⚡ TARGET roles
- Ignore 🟡 SELECTIVE unless pipeline is low
""")

st.success("Daily brief mode active — focus on decisions, not browsing.")
