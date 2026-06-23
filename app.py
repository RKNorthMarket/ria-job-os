
import streamlit as st
import requests
import openai

SERPAPI_KEY = st.secrets["SERPAPI_KEY"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

openai.api_key = OPENAI_API_KEY

st.set_page_config(page_title="RIA Job OS", layout="wide")

KEYWORDS = ["ria", "wealth", "operations", "advisor", "client", "crm", "onboarding"]

def fetch_jobs():
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_jobs",
        "q": "RIA VP operations wealth management director",
        "api_key": SERPAPI_KEY
    }
    return requests.get(url, params=params).json().get("jobs_results", [])

def score(job):
    text = (job["title"] + job.get("description","")).lower()
    return sum([4 for k in KEYWORDS if k in text])

def analyze(job, score):
    prompt = f"""
Job: {job['title']}
Company: {job.get('company_name')}
Score: {score}

Explain fit, risks, and recommendation (APPLY / PASS).
"""

    res = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res["choices"][0]["message"]["content"]

st.title("🧠 RIA Executive Job OS")

if st.button("Run Scan"):

    jobs = fetch_jobs()

    results = []

    for j in jobs:
        s = score(j)
        analysis = analyze(j, s)
        results.append((s, j, analysis))

    results.sort(reverse=True, key=lambda x: x[0])

    for s, j, analysis in results[:10]:

        st.markdown("---")
        st.subheader(j["title"])
        st.write(j.get("company_name"))
        st.write(f"Score: {s}")

        st.write(analysis)

        link = j.get("apply_options", [{}])[0].get("link", "")
        if link:
            st.markdown(f"[Apply Here]({link})")
