import streamlit as st
import requests
import re
import numpy as np

# ----------------------------
# APP
# ----------------------------

st.title("🧠 RIA Executive OS (Real Jobs + Offline Intelligence v22)")

st.write("""
✔ Real job ingestion (ATS feeds)  
✔ Active job URLs (no placeholders)  
✔ Offline scoring engine  
✔ No API costs  
✔ Independent RIA discovery restored  
""")

# ----------------------------
# INDEPENDENT RIA KEYWORDS
# ----------------------------

RIA_KEYWORDS = [
    "ria", "wealth", "advisor", "custody", "clearing",
    "registered investment", "financial advisor", "asset management",
    "operations", "client service", "onboarding"
]

TARGET_TITLES = [
    "director", "head", "vp", "vice president", "manager",
    "operations", "client service", "service", "platform"
]

# ----------------------------
# ATS INGESTION (FREE PUBLIC SOURCES)
# ----------------------------

def fetch_greenhouse_jobs(company_board):
    try:
        url = f"https://boards-api.greenhouse.io/v1/boards/{company_board}/jobs"
        return requests.get(url, timeout=10).json().get("jobs", [])
    except:
        return []


def fetch_lever_jobs(company):
    try:
        url = f"https://api.lever.co/v0/postings/{company}?mode=json"
        return requests.get(url, timeout=10).json()
    except:
        return []

# ----------------------------
# SAMPLE REAL COMPANIES (EXPANDABLE)
# ----------------------------

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

# ----------------------------
# NORMALIZE JOBS
# ----------------------------

def normalize_greenhouse(job):
    return {
        "title": job.get("title"),
        "company": job.get("company_name", "Unknown"),
        "description": job.get("content", ""),
        "link": job.get("absolute_url")
    }


def normalize_lever(job):
    return {
        "title": job.get("text"),
        "company": job.get("company"),
        "description": job.get("descriptionPlain"),
        "link": job.get("hostedUrl")
    }

# ----------------------------
# INGEST ALL JOBS
# ----------------------------

def ingest_jobs():

    jobs = []

    for board in GREENHOUSE_BOARDS:
        raw = fetch_greenhouse_jobs(board)
        jobs += [normalize_greenhouse(j) for j in raw]

    for company in LEVER_BOARDS:
        raw = fetch_lever_jobs(company)
        jobs += [normalize_lever(j) for j in raw]

    # filter broken entries
    jobs = [j for j in jobs if j.get("title") and j.get("link")]

    return jobs

# ----------------------------
# OFFLINE SCORING ENGINE
# ----------------------------

def score_job(job):

    text = f"{job['title']} {job['description']}".lower()

    score = 0

    # title strength
    if any(t in text for t in TARGET_TITLES):
        score += 25

    # RIA relevance
    if any(k in text for k in RIA_KEYWORDS):
        score += 35

    # seniority boost
    if "director" in text:
        score += 15
    if "head" in text:
        score += 15
    if "vp" in text or "vice president" in text:
        score += 20

    # operations relevance
    if "operations" in text:
        score += 10
    if "client" in text:
        score += 10

    return min(score, 100)

# ----------------------------
# LABELS
# ----------------------------

def label(score):

    if score >= 75:
        return "🔥 ELITE TARGET"
    if score >= 60:
        return "⚡ STRONG TARGET"
    if score >= 45:
        return "🟡 MODERATE"
    return "🔵 LOW"

# ----------------------------
# RUN APP
# ----------------------------

st.subheader("📡 Live RIA Job Feed (ATS Ingestion)")

with st.spinner("Fetching real jobs from RIA platforms..."):

    jobs = ingest_jobs()

if not jobs:
    st.error("No jobs returned from ATS feeds. Try again later.")
    st.stop()

ranked = []

for job in jobs:
    score = score_job(job)
    ranked.append((score, job))

ranked.sort(reverse=True, key=lambda x: x[0])

# ----------------------------
# OUTPUT
# ----------------------------

st.subheader("🎯 Ranked Real Opportunities")

for score, job in ranked[:50]:

    st.markdown(f"### {job['title']}")
    st.write(f"🏢 {job['company']}")
    st.write(f"🔗 {job['link']}")

    st.write(f"🎯 Score: {round(score,1)} / 100")
    st.write(f"📊 Label: {label(score)}")

    st.write(job["description"][:400] + "...")

    st.divider()

# ----------------------------
# STATUS
# ----------------------------

st.success("Live ATS ingestion + offline scoring active")
