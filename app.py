import streamlit as st
import requests
from urllib.parse import quote

st.title("🧠 RIA Executive Job OS (Free Version)")

st.write("""
This version uses curated job search links (no APIs required).
Click a category to open live job results.
""")

roles = {
    "Director of Operations (Wealth Management)": "Director of Operations wealth management",
    "VP Operations (RIA / Advisory)": "VP Operations RIA wealth management",
    "Head of Operations": "Head of Operations wealth management RIA",
    "Client Service Director": "Client Service Director wealth management",
    "Practice Management": "Practice Management financial advisory",
    "Advisor Experience": "Advisor Experience wealth management"
}

st.subheader("📌 Target Role Searches")

for label, query in roles.items():
    url = f"https://www.google.com/search?q={quote(query + ' jobs')}"
    st.markdown(f"### {label}")
    st.markdown(f"[View Jobs →]({url})")

st.divider()

st.subheader("🎯 Strategy Filter")

st.write("""
Focus areas:
- RIAs (Registered Investment Advisors)
- Wealth management firms
- Custody / clearing firms
- Advisor platforms
- Fintech servicing advisors

Target compensation: $150k–$200k+
Titles: Director, VP, Head of Operations, COO (smaller firms)
""")

       
