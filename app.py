import streamlit as st
from urllib.parse import quote

st.title("🧠 RIA Executive Job OS (Conversion + Positioning Engine)")

st.write("""
Optimized for:
- RIAs ($500M+ proxy)
- Interview conversion probability
- Role-specific positioning strategy (Balanced Ops + Client Experience narrative)
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
# POSITIONING ENGINE (NEW CORE)
# ----------------------------

def positioning_statement(label):
    l = label.lower()

    # Balanced narrative (Ops + Client Experience)

    if "vp" in l:
        return (
            "Position as: scaled wealth operations leader bridging platform efficiency "
            "and advisor/client experience across complex RIA environments."
        )

    if "director" in l:
        return (
            "Position as: operational owner with strong execution discipline across "
            "advisor servicing, workflow optimization, and scalable operating models."
        )

    if "head" in l or "coo" in l:
        return (
            "Position as: enterprise operator driving organizational design, scale, "
            "and advisor/client experience transformation across multi-office RIAs."
        )

    return (
        "Position as: hybrid operations + client experience leader focused on "
        "scaling advisor support and improving operational efficiency."
    )

# ----------------------------
# UI
# ----------------------------

st.subheader("📊 Conversion + Positioning Output")

for label, query in roles.items():

    url = f"https://www.google.com/search?q={quote(query + ' $500M AUM jobs')}"

    tier = comp_tier(label)
    conv = conversion_score(label)
    conv_label = conversion_label(conv)
    position = positioning_statement(label)

    st.markdown(f"### {label}")
    st.markdown(f"[View Jobs →]({url})")

    st.write(tier)
    st.write(f"🎯 Conversion Score: {conv}/7")
    st.write(conv_label)
    st.write(f"🧠 Positioning: {position}")

st.divider()

# ----------------------------
# EXECUTION RULES
# ----------------------------

st.subheader("⚡ Execution Logic")

st.write("""
1. Focus: 🔥 HIGH CONVERSION roles first  
2. Apply only when positioning statement is clear  
3. Use positioning language in resume + recruiter calls  
4. Avoid generic “operations” framing — always tie to:
   - advisor experience
   - scalability
   - platform transformation
""")

st.success("System now optimized for interview conversion + positioning alignment.")
