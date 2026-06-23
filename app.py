import streamlit as st
import numpy as np
import os
from openai import OpenAI

# ----------------------------
# CONFIG
# ----------------------------

st.title("🧠 RIA Executive OS (Rate-Limit Safe v20)")

st.write("""
Stable architecture:

✔ NO OpenAI calls at startup  
✔ Lazy embedding execution only when needed  
✔ Rate-limit safe design  
✔ Streamlit-safe execution model  
✔ Deterministic scoring  
""")

# ----------------------------
# OPENAI CLIENT
# ----------------------------

if not os.getenv("OPENAI_API_KEY"):
    st.error("Missing OPENAI_API_KEY in Streamlit Secrets")
    st.stop()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------------------------
# RESUME TEXT (STATIC)
# ----------------------------

RESUME_TEXT = """
RIA operations executive with 20+ years experience across Goldman Sachs,
BNY Mellon, State Street, Fidelity Investments.

Expert in onboarding, custody operations, client service,
KPI systems, workflow design, and enterprise transformation.
"""

# ----------------------------
# SAFE EMBEDDING FUNCTION (NO STARTUP CALLS)
# ----------------------------

def get_embedding(text):

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return np.array(response.data[0].embedding)

# ----------------------------
# RESUME EMBEDDING (LAZY + BUTTON TRIGGERED)
# ----------------------------

if "resume_emb" not in st.session_state:
    st.session_state.resume_emb = None

def load_resume_embedding():

    if st.session_state.resume_emb is None:
        st.session_state.resume_emb = get_embedding(RESUME_TEXT)

    return st.session_state.resume_emb

# ----------------------------
# JOB DATA (SAFE MOCK FOR STABILITY)
# ----------------------------

jobs = [
    {
        "title": "Director of Operations",
        "company": "Creative Planning",
        "description": "Lead RIA operations and advisor onboarding strategy.",
        "link": "https://example.com"
    },
    {
        "title": "Head of Client Service",
        "company": "Hightower Advisors",
        "description": "Oversee advisor servicing and client experience.",
        "link": "https://example.com"
    },
    {
        "title": "VP Operations",
        "company": "Fidelity Wealth",
        "description": "Manage wealth platform operations and workflows.",
        "link": "https://example.com"
    }
]

# ----------------------------
# LAZY JOB EMBEDDING CACHE
# ----------------------------

if "job_embeddings" not in st.session_state:
    st.session_state.job_embeddings = {}

def get_job_embedding(job):

    key = f"{job['company']}::{job['title']}"

    if key in st.session_state.job_embeddings:
        return st.session_state.job_embeddings[key]

    emb = get_embedding(f"{job['title']} {job['description']} {job['company']}")
    st.session_state.job_embeddings[key] = emb

    return emb

# ----------------------------
# COSINE SIMILARITY
# ----------------------------

def cosine_similarity(a, b):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    return float(np.dot(a, b))

# ----------------------------
# SCORING ENGINE (SAFE)
# ----------------------------

def score_job(job):

    resume_emb = load_resume_embedding()
    job_emb = get_job_embedding(job)

    return cosine_similarity(resume_emb, job_emb) * 100

# ----------------------------
# UI CONTROL (CRITICAL FIX)
# ----------------------------

st.subheader("📡 RIA Job Engine (Safe Mode)")

# BUTTON TRIGGERS EMBEDDINGS (NOT AUTO-RUN)
if st.button("Run Matching Engine"):

    with st.spinner("Computing semantic matches (may take a few seconds)..."):

        results = []

        for job in jobs:
            try:
                score = score_job(job)
                results.append((score, job))
            except Exception as e:
                st.warning(f"Skipped job due to error: {e}")

        results.sort(reverse=True, key=lambda x: x[0])

        st.subheader("🎯 Ranked Roles")

        for score, job in results:

            st.markdown(f"### {job['title']}")
            st.write(f"🏢 {job['company']}")
            st.write(f"🔗 {job['link']}")

            st.write(f"🎯 Score: {round(score,1)} / 100")

            st.write(job["description"])

            st.divider()

# ----------------------------
# STATUS
# ----------------------------

st.subheader("⚡ System Status")

st.write("""
✔ No OpenAI calls during startup  
✔ Embeddings only triggered by user action  
✔ Rate-limit safe architecture  
✔ Session-cached embeddings  
✔ Stable Streamlit execution model  
""")

st.success("RIA Safe Engine v20 ready")
