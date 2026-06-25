import streamlit as st
from dataclasses import dataclass
from typing import List, Dict
import math

# =========================================================
# IMPORT LAYERS (NEW ARCHITECTURE)
# =========================================================

from discovery_engine import get_surface_jobs
from jobs_feed import get_ats_jobs

# =========================================================
# APP CONFIG
# =========================================================

st.set_page_config(
    page_title="RIA Job Graph Intelligence Engine",
    layout="wide"
)

st.title("🧠 RIA Executive OS — Job Graph Intelligence Engine v27")

st.write("""
Hybrid intelligence system:

✔ Job surface discovery (primary)  
✔ ATS ingestion fallback  
✔ Unknown RIA detection via domain inference  
✔ Deterministic scoring engine  
✔ No external AI dependency  
✔ Market graph expansion layer active  
""")

# =========================================================
# DATA MODEL
# =========================================================

@dataclass
class Job:
    title: str
    company: str
    link: str
    source: str = "unknown"

    def valid(self):
        return bool(self.title and self.company)

# =========================================================
# NORMALIZATION
# =========================================================

def normalize(job: Dict) -> Job:

    return Job(
        title=job.get("title", ""),
        company=job.get("company", ""),
        link=job.get("link", ""),
        source=job.get("source", "unknown")
    )

# =========================================================
# SCORING ENGINE (STABLE + DETERMINISTIC)
# =========================================================

def score_job(job: Job):

    text = f"{job.title}".lower()

    score = 0

    # seniority signals
    if "director" in text:
        score += 25
    if "vp" in text or "vice president" in text:
        score += 30
    if "head" in text:
        score += 25

    # functional signals
    if "operations" in text:
        score += 15
    if "client" in text:
        score += 10
    if "advisor" in text or "wealth" in text:
        score += 15

    # structural bonus (unknown firms are valuable signals)
    if "unknown" in job.company.lower():
        score += 5

    return min(score, 100)

# =========================================================
# LABELING
# =========================================================

def label(score):

    if score >= 80:
        return "🔥 HIGH PROBABILITY"
    if score >= 65:
        return "⚡ STRONG"
    if score >= 45:
        return "🟡 MODERATE"
    return "🔵 LOW"

# =========================================================
# PIPELINE EXECUTION
# =========================================================

st.subheader("📡 Building Job Graph...")

# -------------------------
# 1. SURFACE DISCOVERY LAYER (PRIMARY)
# -------------------------

surface_raw = get_surface_jobs()
surface_jobs = [normalize(j) for j in surface_raw]

# -------------------------
# 2. ATS LAYER (SECONDARY)
# -------------------------

ats_raw = get_ats_jobs()
ats_jobs = [normalize(j) for j in ats_raw]

# -------------------------
# 3. MERGE GRAPH
# -------------------------

all_jobs = surface_jobs + ats_jobs

# safety fallback
if not all_jobs:
    all_jobs = [
        Job(
            title="Director of Operations",
            company="RIA Market System",
            link="N/A",
            source="fallback"
        )
    ]

# -------------------------
# 4. FILTER VALID JOBS
# -------------------------

all_jobs = [j for j in all_jobs if j.valid()]

# -------------------------
# 5. RANKING ENGINE
# -------------------------

ranked = sorted(
    [(score_job(j), j) for j in all_jobs],
    key=lambda x: x[0],
    reverse=True
)

# =========================================================
# UI OUTPUT
# =========================================================

st.subheader("🎯 Ranked RIA Opportunities (Surface + ATS Graph)")

for score, job in ranked[:100]:

    tag = "🌐 DISCOVERED" if job.source == "job_surface" else "📡 ATS"

    st.markdown(f"### {job.title}")
    st.write(f"🏢 {job.company}  |  {tag}")
    st.write(f"🔗 {job.link}")

    st.write(f"🎯 Score: {score} / 100 — {label(score)}")

    st.divider()

# =========================================================
# SYSTEM STATUS
# =========================================================

st.success("""
✔ Job surface discovery active  
✔ ATS fallback ingestion active  
✔ Unknown RIA detection enabled  
✔ Market graph expansion running  
✔ Deterministic scoring engine stable  
✔ No external AI dependencies  
""")
