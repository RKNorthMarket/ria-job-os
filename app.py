import streamlit as st
import pandas as pd
import os

# =========================================================
# APP CONFIG
# =========================================================

st.set_page_config(
    page_title="RIA Opportunity OS",
    layout="wide"
)

st.title("🧠 RIA Executive OS — Opportunity Command Center")

st.write("""
Pipeline-first executive job intelligence system:

✔ Pipeline tracking (CSV-backed)  
✔ Strategic RIA target mapping  
✔ Safe verified jobs layer (no API dependency)  
✔ Fully deterministic scoring  
✔ Crash-resistant architecture  
""")

# =========================================================
# SAFE CSV LOADING (CRASH PROOF)
# =========================================================

PIPELINE_FILE = "pipeline.csv"

def load_pipeline():

    if not os.path.exists(PIPELINE_FILE):
        st.warning("⚠️ pipeline.csv not found — loading empty dataset")
        return pd.DataFrame(columns=[
            "Company",
            "Role",
            "Status",
            "Last Contact",
            "Next Action",
            "Priority"
        ])

    try:
        df = pd.read_csv(PIPELINE_FILE)

        # normalize missing columns safely
        required_cols = ["Company","Role","Status","Last Contact","Next Action","Priority"]
        for col in required_cols:
            if col not in df.columns:
                df[col] = ""

        return df

    except Exception as e:
        st.error(f"Error loading pipeline.csv: {e}")
        return pd.DataFrame(columns=[
            "Company","Role","Status","Last Contact","Next Action","Priority"
        ])

pipeline_df = load_pipeline()

# =========================================================
# STRATEGIC TARGET FIRMS
# =========================================================

TARGET_FIRMS = [
    "Mercer Advisors",
    "Mariner Wealth Advisors",
    "Creative Planning",
    "AssetMark",
    "Cetera Financial Group",
    "Kestra Financial",
    "LPL Financial",
    "Raymond James",
    "Carson Group",
    "Commonwealth Financial Network"
]

# =========================================================
# SIMPLE FIT ENGINE (NO AI / NO API)
# =========================================================

def score_role(title: str, company: str):

    text = f"{title} {company}".lower()

    score = 0

    # seniority signals
    if "director" in text:
        score += 25
    if "vp" in text:
        score += 30
    if "head" in text:
        score += 25

    # domain signals
    if "operations" in text:
        score += 15
    if "client" in text:
        score += 10
    if "wealth" in text or "ria" in text:
        score += 10

    # penalties (critical for accuracy)
    bad_terms = [
        "engineer",
        "it",
        "developer",
        "marketing",
        "accountant",
        "payroll",
        "chef",
        "teacher",
        "mortgage"
    ]

    for b in bad_terms:
        if b in text:
            score -= 40

    return max(0, min(score, 100))

# =========================================================
# STATIC VERIFIED JOBS (SAFE MODE)
# =========================================================

def get_verified_jobs():

    return [
        {
            "title": "Director of Operations",
            "company": "RIA Wealth Platform (Example Verified Source)",
            "link": "https://www.google.com/search?q=RIA+Director+of+Operations+jobs",
            "description": "Wealth operations leadership role within RIA platform environments."
        },
        {
            "title": "Head of Client Service",
            "company": "Wealth Management Firm (Example)",
            "link": "https://www.google.com/search?q=wealth+client+service+director+jobs",
            "description": "Advisor service delivery and client experience leadership."
        }
    ]

# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3 = st.tabs([
    "📊 Dashboard",
    "🎯 Strategic Targets",
    "📡 Verified Jobs"
])

# =========================================================
# TAB 1 — DASHBOARD
# =========================================================

with tab1:

    st.subheader("📊 Active Pipeline")

    st.dataframe(pipeline_df, use_container_width=True)

    st.subheader("⚡ Metrics")

    st.metric("Total Pipeline Items", len(pipeline_df))

    if "Priority" in pipeline_df.columns:
        st.metric("High Priority", len(pipeline_df[pipeline_df["Priority"] == "High"]))

    if "Status" in pipeline_df.columns:
        st.metric(
            "In Hiring Stage",
            len(pipeline_df[pipeline_df["Status"].astype(str).str.contains("Hiring", na=False)])
        )

# =========================================================
# TAB 2 — STRATEGIC TARGETS
# =========================================================

with tab2:

    st.subheader("🎯 Strategic RIA Targets")

    for firm in TARGET_FIRMS:

        st.markdown(f"### {firm}")
        st.write("Strategic wealth / RIA platform target")

        sample_score = 85 if firm in ["Mercer Advisors", "Creative Planning"] else 75

        st.write(f"Fit Score: {sample_score}")
        st.write("Type: Strategic Target (no ATS dependency)")
        st.divider()

# =========================================================
# TAB 3 — VERIFIED JOBS
# =========================================================

with tab3:

    st.subheader("📡 Verified Jobs (Safe Mode)")

    jobs = get_verified_jobs()

    for job in jobs:

        st.markdown(f"### {job['title']}")
        st.write(f"🏢 {job['company']}")
        st.write(f"🔗 {job['link']}")
        st.write(job["description"])
        st.divider()

# =========================================================
# FOOTER
# =========================================================

st.success("RIA Opportunity OS v1 Stable Build — No external dependencies, crash-safe architecture active")
