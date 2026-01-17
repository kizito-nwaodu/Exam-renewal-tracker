import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIG ---
TRANSCRIPT_ID = "dz336sng53l39pp"
URL = f"https://learn.microsoft.com/api/profiles/transcript/share/{TRANSCRIPT_ID}"

st.set_page_config(page_title="MS Learning & Cert Tracker", layout="wide")
st.title("🎓 Microsoft Learning & Certification Tracker")

def fetch_data():
    try:
        response = requests.get(URL)
        return response.json() if response.status_code == 200 else None
    except: return None

data = fetch_data()

if data:
    # 1. SUMMARY STATS (From the data you shared)
    col1, col2, col3 = st.columns(3)
    col1.metric("Modules Completed", data.get("totalModulesCompleted", 0))
    col2.metric("Learning Paths", data.get("totalLearningPathsCompleted", 0))
    col3.metric("Study Hours", round(data.get("totalTrainingMinutes", 0) / 60, 1))

    # 2. CERTIFICATION TRACKING
    st.subheader("🛡️ Renewal Tracker")
    cert_data = data.get("certificationData", {})
    active_certs = cert_data.get("activeCertifications", [])
    
    if not active_certs:
        st.warning("⚠️ No Certifications found in JSON. Please check your Microsoft Learn Transcript settings and ensure 'Certifications' is checked in the 'Include in share' section.")
    else:
        # (Rest of the renewal logic from previous steps goes here)
        st.write("Certs found! Processing...")

    # 3. RECENT MODULES (For visibility)
    st.subheader("📚 Recent Training")
    modules = data.get("modulesCompleted", [])[:5]
    if modules:
        for m in modules:
            st.write(f"- **{m['title']}** (Completed: {m['completedOn'][:10]})")

else:
    st.error("Could not fetch data. Check your Transcript ID.")
