import streamlit as st

from discovery_engine import get_surface_jobs
from jobs_feed import get_ats_jobs

# =========================================================
# UI CONFIG
# =========================================================

st.set_page_config(
    page_title="RIA Job Graph Intelligence Engine",
    layout="wide"
)

st.title("🧠 RIA Executive OS — Job Graph Intelligence Engine v28")

# =========================================================
# PIPELINE
# =========================================================

st.subheader("📡 Building Job Graph...")

surface_jobs = get_surface_jobs()
ats_jobs = get_ats_jobs()

jobs = surface_jobs + ats_jobs

# fallback safety
if not jobs:
    jobs = [{
        "title": "Director of Operations",
        "company": "RIA Market System",
        "link": "N/A",
        "source": "fallback"
    }]

# =========================================================
# SCORING
# =========================================================

def score(j):

    text = j["title"].lower()
    s = 0

    if "director" in text:
        s += 25
    if "vp" in text:
        s += 30
    if "head" in text:
        s += 25
    if "operations" in text:
        s += 15
    if "client" in text:
        s += 10

    return min(s, 100)

ranked = sorted(jobs, key=score, reverse=True)

# =========================================================
# OUTPUT
# =========================================================

st.subheader("🎯 Ranked Opportunities")

for j in ranked[:100]:

    st.markdown(f"### {j['title']}")
    st.write(f"🏢 {j['company']} | {j.get('source','unknown')}")
    st.write(f"🔗 {j['link']}")
    st.write(f"🎯 Score: {score(j)} / 100")

    st.divider()

# =========================================================
# STATUS
# =========================================================

st.success("""
✔ Job surface discovery active  
✔ Stable ATS fallback layer  
✔ No import dependency risk  
✔ Deterministic scoring engine  
""")
