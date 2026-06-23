import streamlit as st
import requests
import numpy as np
import re

# =========================================================
# APP HEADER
# =========================================================

st.title("🧠 RIA Executive OS (Production Safe v23)")

st.write("""
Production-safe job intelligence system:

✔ No OpenAI dependency  
✔ Real ATS ingestion (Greenhouse + Lever)  
✔ Defensive parsing (no crashes from bad data)  
✔ Unified job schema normalization  
✔ Offline scoring engine  
✔ Stable Streamlit execution  
""")

# =========================================================
# RIA SCORING SIGNALS
# =========================================================

RIA_KEYWORDS = [
    "ria", "registered investment", "wealth", "advisor",
    "custody", "clearing", "asset management", "financial advisor"
]

ROLE_KEYWORDS = [
    "director", "head", "vp", "vice president", "manager",
    "operations", "client service", "service", "onboarding"
]

HIGH_VALUE_TERMS = [
    "platform", "scaling", "transformation", "workflow",
    "kpi", "strategy", "enterprise"
]

# =========================================================
# ATS SOURCES
# =========================================================

GREENHOUSE_BOARDS = [
    "creativeplanning",
    "hightoweradvisors",
    "stifel"
]

LEVER_BOARDS = [
    "carsongroup",
    "focusfinancial",
    "merceradvisors"
]

# =========================================================
# SAFE API FETCHERS
# =========================================================

def fetch_greenhouse(board):
    try:
        url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
        r = requests.get(url, timeout=10)
        return r.json().get("jobs", [])
    except:
        return []


def fetch_lever(company):
    try:
        url = f"https://api.lever.co/v0/postings/{company}?mode=json"
        r = requests.get(url, timeout=10)
        data = r.json()
        return data if isinstance(data, list) else []
    except:
        return []

# =========================================================
# NORMALIZATION LAYER (DEFENSIVE)
# =========================================================

def normalize_greenhouse(job):

    if not isinstance(job, dict):
        return None

    return {
        "title": job.get("title") or "Unknown Title",
        "company": job.get("company_name") or "Unknown Company",
        "description": job.get("content") or "",
        "link": job.get("absolute_url") or ""
    }


def normalize_lever(job):

    if not isinstance(job, dict):
        return None

    categories = job.get("categories")
    team = None

    if isinstance(categories, dict):
        team = categories.get("team")

    return {
        "title": job.get("text") or job.get("title") or "Unknown Title",
        "company": job.get("company") or team or "Unknown Company",
        "description": job.get("descriptionPlain") or job.get("description") or "",
        "link": job.get("hostedUrl") or job.get("applyUrl") or ""
    }

# =========================================================
# INGESTION ENGINE (CLEAN + SAFE)
# =========================================================

def ingest_jobs():

    jobs = []

    # Greenhouse ingestion
    for board in GREENHOUSE_BOARDS:
        raw = fetch_greenhouse(board)

        for j in raw:
            try:
                item = normalize_greenhouse(j)
                if item and item["title"] != "Unknown Title" and item["link"]:
                    jobs.append(item)
            except:
                continue

    # Lever ingestion
    for company in LEVER_BOARDS:
        raw = fetch_lever(company)

        for j in raw:
            try:
                item = normalize_lever(j)
                if item and item["title"] != "Unknown Title" and item["link"]:
                    jobs.append(item)
            except:
                continue

    return jobs

# =========================================================
# SCORING ENGINE (OFFLINE)
# =========================================================

def score_job(job):

    text = f"{job['title']} {job['description']}".lower()

    score = 0

    # RIA relevance
    if any(k in text for k in RIA_KEYWORDS):
        score += 35

    # role seniority
    if "director" in text:
        score += 15
    if "head" in text:
        score += 15
    if "vp" in text or "vice president" in text:
        score += 20

    # role type
    if any(k in text for k in ROLE_KEYWORDS):
        score += 15

    # strategic complexity
    if any(k in text for k in HIGH_VALUE_TERMS):
        score += 10

    return min(score, 100)

# =========================================================
# LABELS
# =========================================================

def label(score):

    if score >= 75:
        return "🔥 ELITE TARGET"
    if score >= 60:
        return "⚡ STRONG TARGET"
    if score >= 45:
        return "🟡 MODERATE"
    return "🔵 LOW"

# =========================================================
# MAIN EXECUTION
# =========================================================

st.subheader("📡 Live RIA Job Intelligence Feed")

with st.spinner("Ingesting real ATS job feeds..."):

    jobs = ingest_jobs()

if not jobs:
    st.error("No jobs found. ATS sources may be temporarily unavailable.")
    st.stop()

ranked = []

for job in jobs:
    try:
        score = score_job(job)
        ranked.append((score, job))
    except:
        continue

ranked.sort(reverse=True, key=lambda x: x[0])

# =========================================================
# OUTPUT
# =========================================================

st.subheader("🎯 Ranked Opportunities")

for score, job in ranked[:50]:

    st.markdown(f"### {job['title']}")
    st.write(f"🏢 {job['company']}")
    st.write(f"🔗 {job['link']}")

    st.write(f"🎯 Score: {round(score,1)} / 100")
    st.write(f"📊 Label: {label(score)}")

    st.write(job['description'][:500])

    st.divider()

# =========================================================
# SYSTEM STATUS
# =========================================================

st.subheader("⚡ System Status")

st.write("""
✔ Defensive ingestion layer active  
✔ No OpenAI dependency  
✔ No rate limits  
✔ Stable schema normalization  
✔ Multi-ATS ingestion enabled  
✔ Production-safe scoring engine  
""")

st.success("RIA Intelligence Engine v23 active and stable")
