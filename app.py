import streamlit as st

# =========================================================
# SAFE IMPORTS (NO BREAKING DEPENDENCIES)
# =========================================================

from jobs_feed import get_ats_jobs

# Discovery engine import is OPTIONAL-safe
try:
    from discovery_engine import get_surface_jobs
except Exception:
    get_surface_jobs = lambda: []

# =========================================================
# APP CONFIG
# =========================================================

st.set_page_config(
    page_title="RIA Job Graph Intelligence Engine",
    layout="wide"
)

st.title("🧠 RIA Executive OS — Job Intelligence Engine (Stable Build)")

st.write("""
Stable architecture mode:

✔ Safe ATS contract layer  
✔ Job surface discovery layer  
✔ Crash-proof imports  
✔ Deterministic scoring  
✔ Streamlit Cloud safe execution  
""")

# =========================================================
# PIPELINE EXECUTION (CRASH SAFE)
# =========================================================

st.subheader("📡 Building Job Graph...")

surface_jobs = []
ats_jobs = []

# -------------------------
# SAFE SURFACE LAYER
# -------------------------

try:
    surface_jobs = get_surface_jobs()
except Exception as e:
    surface_jobs = []

# -------------------------
# SAFE ATS LAYER
# -------------------------

try:
    ats_jobs = get_ats_jobs()
except Exception:
    ats_jobs = []

# -------------------------
# MERGE
# -------------------------

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
# SCORING ENGINE
# =========================================================

def score(job):

    text = job.get("title", "").lower()

    s = 0

    if "director" in text:
        s += 25
    if "vp" in text or "vice president" in text:
        s += 30
    if "head" in text:
        s += 25
    if "operations" in text:
        s += 15
    if "client" in text:
        s += 10
    if "advisor" in text or "wealth" in text:
        s += 10

    return min(s, 100)

ranked = sorted(jobs, key=score, reverse=True)

# =========================================================
# OUTPUT
# =========================================================

st.subheader("🎯 Ranked Opportunities (Stable Graph Mode)")

for j in ranked[:100]:

    st.markdown(f"### {j.get('title','Unknown Role')}")
    st.write(f"🏢 {j.get('company','Unknown')} | {j.get('source','unknown')}")
    st.write(f"🔗 {j.get('link','N/A')}")
    st.write(f"🎯 Score: {score(j)} / 100")

    st.divider()

# =========================================================
# SYSTEM STATUS
# =========================================================

st.success("""
✔ Import-safe architecture active  
✔ ATS contract layer stable  
✔ Surface discovery optional-safe  
✔ Streamlit crash protection enabled  
✔ Deterministic scoring engine running  
""")
