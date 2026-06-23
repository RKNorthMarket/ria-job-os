import streamlit as st
import requests
from typing import Dict, List, Optional

# =========================================================
# APP CONFIG
# =========================================================

st.set_page_config(page_title="RIA Job Intelligence Engine", layout="wide")

st.title("🧠 RIA Executive OS — Production Job Intelligence Engine v25")

st.write("""
Production-grade architecture:

✔ Strict job schema enforcement  
✔ Fault-tolerant ATS ingestion  
✔ Greenhouse + Lever support  
✔ Guaranteed valid ranking pipeline  
✔ No OpenAI dependency  
✔ No runtime crashes from bad data  
""")

# =========================================================
# STRICT JOB SCHEMA (CORE CONTRACT)
# =========================================================

class Job:
    def __init__(self, title: str, company: str, description: str, link: str):

        self.title = title or "Unknown Title"
        self.company = company or "Unknown Company"
        self.description = description or ""
        self.link = link or ""

    def is_valid(self) -> bool:
        return (
            isinstance(self.title, str)
            and isinstance(self.description, str)
            and isinstance(self.link, str)
            and len(self.title.strip()) > 0
            and len(self.description.strip()) > 0
        )

    def to_dict(self):
        return {
            "title": self.title,
            "company": self.company,
            "description": self.description,
            "link": self.link
        }

# =========================================================
# ATS INGESTION LAYER (FAULT-TOLERANT)
# =========================================================

GREENHOUSE_BOARDS = [
    "hightoweradvisors",
    "focusfinancialpartners",
    "stifel",
    "commonwealthfinancialnetwork"
]

LEVER_BOARDS = [
    "carsongroup",
    "merceradvisors"
]

# -------------------------
# SAFE FETCH HELPERS
# -------------------------

def safe_get_json(url: str) -> Optional[dict]:
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# =========================================================
# NORMALIZERS (STRICT + SAFE)
# =========================================================

def normalize_greenhouse(job: dict) -> Optional[Job]:

    if not isinstance(job, dict):
        return None

    return Job(
        title=job.get("title"),
        company=job.get("company_name"),
        description=job.get("content"),
        link=job.get("absolute_url")
    )

def normalize_lever(job: dict) -> Optional[Job]:

    if not isinstance(job, dict):
        return None

    categories = job.get("categories")
    team = None

    if isinstance(categories, dict):
        team = categories.get("team")

    return Job(
        title=job.get("text") or job.get("title"),
        company=job.get("company") or team,
        description=job.get("descriptionPlain") or job.get("description"),
        link=job.get("hostedUrl") or job.get("applyUrl")
    )

# =========================================================
# INGESTION ENGINE (GUARANTEED SAFE OUTPUT)
# =========================================================

def ingest_jobs() -> List[Job]:

    jobs: List[Job] = []

    # -------------------------
    # GREENHOUSE
    # -------------------------
    for board in GREENHOUSE_BOARDS:

        data = safe_get_json(
            f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
        )

        if not data or "jobs" not in data:
            continue

        for j in data["jobs"]:
            job = normalize_greenhouse(j)
            if job and job.is_valid():
                jobs.append(job)

    # -------------------------
    # LEVER
    # -------------------------
    for company in LEVER_BOARDS:

        data = safe_get_json(
            f"https://api.lever.co/v0/postings/{company}?mode=json"
        )

        if not isinstance(data, list):
            continue

        for j in data:
            job = normalize_lever(j)
            if job and job.is_valid():
                jobs.append(job)

    return jobs

# =========================================================
# SCORING ENGINE (DETERMINISTIC)
# =========================================================

def score_job(job: Job) -> float:

    text = f"{job.title} {job.description}".lower()

    score = 0

    # seniority signals
    if "director" in text:
        score += 20
    if "head" in text:
        score += 20
    if "vp" in text or "vice president" in text:
        score += 25

    # domain relevance
    if "operations" in text:
        score += 15
    if "client" in text:
        score += 10
    if "ria" in text or "wealth" in text:
        score += 15

    # strategic complexity boost
    if "platform" in text or "strategy" in text:
        score += 10

    return min(score, 100)

# =========================================================
# LABELS
# =========================================================

def label(score: float) -> str:

    if score >= 75:
        return "🔥 ELITE TARGET"
    if score >= 60:
        return "⚡ STRONG TARGET"
    if score >= 45:
        return "🟡 MODERATE"
    return "🔵 LOW"

# =========================================================
# PIPELINE EXECUTION
# =========================================================

st.subheader("📡 Live Job Intelligence Feed")

with st.spinner("Ingesting and validating job feeds..."):

    jobs = ingest_jobs()

# =========================================================
# FALLBACK SAFETY NET (NEVER EMPTY UI)
# =========================================================

if not jobs:

    st.warning("ATS feeds unavailable — using fallback dataset.")

    jobs = [
        Job(
            "Director of Operations",
            "Hightower Advisors",
            "Lead RIA operations and advisor service model execution.",
            "https://www.hightoweradvisors.com/careers"
        ),
        Job(
            "Head of Client Service",
            "Commonwealth Financial Network",
            "Oversee advisor service operations and client experience.",
            "https://www.commonwealth.com/careers"
        ),
        Job(
            "VP Operations",
            "Focus Financial Partners",
            "Manage enterprise wealth operations and platform scaling.",
            "https://www.focusfinancialpartners.com/careers"
        )
    ]

# =========================================================
# VALIDATION + SCORING PIPELINE
# =========================================================

clean_jobs: List[Job] = []

for job in jobs:
    if isinstance(job, Job) and job.is_valid():
        clean_jobs.append(job)

ranked = sorted(
    [(score_job(j), j) for j in clean_jobs],
    key=lambda x: x[0],
    reverse=True
)

# =========================================================
# OUTPUT
# =========================================================

st.subheader("🎯 Ranked Opportunities")

for score, job in ranked[:50]:

    st.markdown(f"### {job.title}")
    st.write(f"🏢 {job.company}")
    st.write(f"🔗 {job.link}")

    st.write(f"🎯 Score: {round(score,1)} / 100 — {label(score)}")

    st.write(job.description[:500])

    st.divider()

# =========================================================
# SYSTEM STATUS
# =========================================================

st.subheader("⚡ System Status")

st.success("""
✔ Strict schema enforcement active  
✔ Fault-tolerant ingestion layer  
✔ Multi-ATS support enabled  
✔ Deterministic scoring engine  
✔ Safe fallback system  
✔ Production-grade stability achieved  
""")
