import streamlit as st
import numpy as np
import re

# ----------------------------
# APP
# ----------------------------

st.title("🧠 RIA Executive OS (Offline Semantic Engine v21)")

st.write("""
Fully offline intelligence system:

✔ No OpenAI API required  
✔ No billing required  
✔ No rate limits  
✔ Instant scoring  
✔ Deterministic semantic matching  
""")

# ----------------------------
# RESUME
# ----------------------------

RESUME_TEXT = """
RIA operations executive with 20+ years experience across Goldman Sachs,
BNY Mellon, State Street, Fidelity Investments.

Expert in onboarding, custody, client service, operations leadership,
KPI systems, workflow design, and RIA platform scaling.
"""

# ----------------------------
# SIMPLE TOKENIZER (FREE SEMANTICS)
# ----------------------------

def tokenize(text):
    return set(re.findall(r"[a-zA-Z]+", text.lower()))

resume_tokens = tokenize(RESUME_TEXT)

# ----------------------------
# JOB DATA (SAMPLE - REPLACE WITH YOUR FEED LATER)
# ----------------------------

jobs = [
    {
        "title": "Director of Operations",
        "company": "Creative Planning",
        "description": "Lead RIA onboarding and advisor operations strategy.",
        "link": "https://example.com"
    },
    {
        "title": "Head of Client Service",
        "company": "Hightower Advisors",
        "description": "Oversee advisor service model and client operations.",
        "link": "https://example.com"
    },
    {
        "title": "VP Operations",
        "company": "Fidelity Wealth",
        "description": "Manage wealth platform operations and service delivery.",
        "link": "https://example.com"
    },
]

# ----------------------------
# OFFLINE SEMANTIC SCORING
# ----------------------------

WEIGHTS = {
    "director": 5,
    "head": 5,
    "vp": 4,
    "operations": 4,
    "client": 3,
    "service": 3,
    "ria": 5,
    "wealth": 3,
    "advisor": 3,
    "onboarding": 4,
    "kpi": 3,
    "strategy": 2,
}

def keyword_score(text):

    text = text.lower()
    score = 0

    for k, w in WEIGHTS.items():
        if k in text:
            score += w

    return score


def similarity_score(job):

    job_text = f"{job['title']} {job['description']} {job['company']}"

    job_tokens = tokenize(job_text)

    overlap = len(resume_tokens.intersection(job_tokens))
    total = len(resume_tokens.union(job_tokens))

    return (overlap / total) * 100 if total > 0 else 0


def final_score(job):

    sim = similarity_score(job)
    kw = keyword_score(f"{job['title']} {job['description']} {job['company']}")

    return (0.7 * sim) + (0.3 * kw * 5)

# ----------------------------
# LABELS
# ----------------------------

def label(score):

    if score >= 70:
        return "🔥 ELITE TARGET"
    if score >= 55:
        return "⚡ STRONG TARGET"
    if score >= 40:
        return "🟡 MODERATE"
    return "🔵 LOW"

# ----------------------------
# RUN ENGINE
# ----------------------------

st.subheader("📡 Offline RIA Job Engine")

ranked = []

for job in jobs:
    score = final_score(job)
    ranked.append((score, job))

ranked.sort(reverse=True, key=lambda x: x[0])

# ----------------------------
# OUTPUT
# ----------------------------

st.subheader("🎯 Ranked Opportunities")

for score, job in ranked:

    st.markdown(f"### {job['title']}")
    st.write(f"🏢 {job['company']}")
    st.write(f"🔗 {job['link']}")

    st.write(f"🎯 Score: {round(score,1)} / 100")
    st.write(f"📊 Label: {label(score)}")

    st.write(job["description"])

    st.divider()

# ----------------------------
# STATUS
# ----------------------------

st.subheader("⚡ System Status")

st.success("""
✔ Fully offline mode active  
✔ No OpenAI dependency  
✔ No billing required  
✔ Stable Streamlit execution  
✔ Deterministic scoring engine  
""")
