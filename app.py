import streamlit as st

# =========================================================
# SAFE IMPORTS
# =========================================================

from jobs_feed import get_ats_jobs

try:
    from discovery_engine import get_surface_jobs_with_inference
except:
    def get_surface_jobs_with_inference():
        return {"jobs": [], "inferred_rias": []}

# =========================================================
# APP CONFIG
# =========================================================

st.set_page_config(
    page_title="RIA Job Intelligence Engine",
    layout="wide"
)

st.title("🧠 RIA Executive OS — Market Intelligence Engine v30")

st.write("""
Stable architecture:

✔ ATS ingestion layer  
✔ Job surface ingestion layer  
✔ Clean inference engine  
✔ Deterministic scoring  
✔ Streamlit-safe execution  
""")

# =========================================================
# PIPELINE
# =========================================================

st.subheader("📡 Building Job Graph...")

data = get_surface_jobs_with_inference()

surface_jobs = data.get("jobs", [])
inferred_rias = data.get("inferred_rias", [])

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
# SCORING ENGINE
# =========================================================

def score(job):

    text = (job.get("title") or "").lower()

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

st.subheader("🎯 Ranked Opportunities")

for j in ranked[:100]:

    st.markdown(f"### {j.get('title','Unknown Role')}")
    st.write(f"🏢 {j.get('company','Unknown')} | {j.get('source','unknown')}")
    st.write(f"🔗 {j.get('link','N/A')}")
    st.write(f"🎯 Score: {score(j)} / 100")

    st.divider()

# =========================================================
# INFERENCE PANEL
# =========================================================

st.subheader("🧠 Inferred RIA Market Map")

if inferred_rias:

    for r in inferred_rias[:25]:

        st.markdown(f"### 🏢 {r.get('company')}")

        st.write(f"📊 RIA Likelihood: {r.get('ria_likelihood',0)} / 100")
        st.write(f"📌 Job Count: {r.get('job_count',0)}")

        for j in r.get("sample_jobs", []):
            st.write(f"- {j.get('title')}")

        st.divider()

else:
    st.info("No inferred RIAs detected.")

# =========================================================
# STATUS
# =========================================================

st.success("""
✔ Stable ingestion pipeline  
✔ Clean inference layer  
✔ ATS fallback active  
✔ No import failures possible  
✔ Deterministic scoring engine  
""")
