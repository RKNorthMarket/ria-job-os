import streamlit as st
from urllib.parse import quote

st.title("🧠 RIA Executive Job OS (Conversion Optimized)")

st.write("""
Optimized for one outcome:  
👉 Increase interview conversion rate for Director / VP / Head of Ops roles in RIAs ($500M+ proxy)
""")

# ----------------------------
# ROLE SET
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
# COMP TIERS (UNCHANGED)
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
# INTERVIEW CONVERSION ENGINE (NEW CORE)
# ----------------------------

def conversion_score(label):
    score = 0
    l = label.lower()

    # seniority alignment
    if "director" in l or "vp" in l or "head" in l:
        score += 3

    # domain alignment (your strongest area)
    if "operations" in l:
        score += 2

    # ria relevance
    if "ria" in l or "wealth" in l:
        score += 2

    # advisor/client exposure advantage
    if "client" in l or "advisor" in l:
        score += 1

    return score

def conversion_label(score):
    if score >= 6:
        return "🔥 HIGH CONVERSION (Strong Interview Probability)"
    if score >= 4:
        return "⚡ MEDIUM CONVERSION (Needs Positioning)"
    return "🟡 LOW CONVERSION (High Effort / Low Yield)"

def positioning_tip(label):
    l = label.lower()

    if "vp" in l:
        return "Position as: platform-scale ops + advisor experience + transformation leadership"
    if "director" in l:
        return "Position as: operational owner with measurable scaling + client impact"
    if "head" in l:
        return "Position as: enterprise operator / org design + execution leader"
    return "Position carefully — likely needs reframing to increase seniority signal"

# ----------------------------
# UI
# ----------------------------

st.subheader("📊 Conversion Optimized Pipeline")

for label, query in roles.items():

    url = f"https://www.google.com/search?q={quote(query + ' $500M AUM jobs')}"

    tier = comp_tier(label)
    conv = conversion_score(label)
    conv_label = conversion_label(conv)
    tip = positioning_tip(label)

    st.markdown(f"### {label}")
    st.markdown(f"[View Jobs →]({url})")

    st.write(tier)
    st.write(f"🎯 Conversion Score: {conv}/7")
    st.write(conv_label)
    st.write(f"🧠 Positioning: {tip}")

st.divider()

# ----------------------------
# EXECUTION RULES (UPDATED)
# ----------------------------

st.subheader("⚡ Conversion Rules")

st.write("""
To maximize interview conversion:

1. Focus ONLY on 🔥 HIGH CONVERSION roles first
2. Apply ONLY when positioning message is clear
3. Avoid 🟡 LOW CONVERSION unless strategically necessary
4. Every application must be framed as:
   - scale operator
   - transformation leader
   - advisor/client experience owner
""")

st.success("Goal: fewer applications → higher interview rate → faster VP/Director placement")
