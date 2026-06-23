import streamlit as st
from urllib.parse import quote

st.title("🧠 RIA Executive Job OS (RIA 500M+ Filter)")

st.write("""
Focused exclusively on:
👉 RIAs & advisory firms with $500M+ AUM (or equivalent scale signals)
👉 Director / VP / Head of Operations roles
""")

queries = [
    "RIA wealth management $500 million AUM Director of Operations",
    "Registered Investment Advisor VP Operations multi office firm",
    "wealth management firm Head of Operations enterprise RIA",
    "independent advisory firm Client Service Director RIA",
    "multi billion AUM RIA operations leadership jobs",
    "wealth management COO or Head of Operations RIA firm"
]

st.subheader("📊 Target RIA Searches (500M+ Filter)")

for q in queries:
    url = f"https://www.google.com/search?q={quote(q + ' jobs')}"
    st.markdown(f"- [{q}]({url})")

st.divider()

st.subheader("🎯 What This Filters For")

st.write("""
We prioritize firms with signals of scale:

✔ $500M+ AUM (explicit or inferred)  
✔ Multi-advisor / multi-office RIAs  
✔ Custodians: Schwab, Fidelity, Pershing, Altruist  
✔ Platform RIAs / aggregator models  
✔ Institutional-grade service operations  

Target roles:
- Director of Operations
- VP Operations
- Head of Client Service
- Head of Advisor Experience
- COO (mid-size RIAs)
""")
