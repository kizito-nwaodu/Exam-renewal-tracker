import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIG ---
TRANSCRIPT_ID = "dz336sng53l39pp"
URL = f"https://learn.microsoft.com/api/profiles/transcript/share/{TRANSCRIPT_ID}"

st.set_page_config(page_title="MS Cert Tracker", layout="wide")
st.title("🛡️ Microsoft Certification Renewal Tracker")

def fetch_data():
    try:
        response = requests.get(URL)
        return response.json() if response.status_code == 200 else None
    except: return None

data = fetch_data()

if data:
    # --- DATA CHECK (Debug) ---
    c_data = data.get("certificationData", {})
    certs = c_data.get("activeCertifications", [])
    exams = data.get("examData", {}).get("passedExams", [])
    
    # UI Notification if nothing is found
    if not certs and not exams:
        st.error("🚨 No certifications or exams found in your transcript data.")
        st.info("Check if your Certification Profile is linked at: https://learn.microsoft.com/users/me/credentials")
    
    # --- PROCESSING ---
    all_items = certs + exams
    cert_list = []

    for item in all_items:
        name = item.get("certificationName") or item.get("examName") or "Unknown"
        raw_issue = item.get("issueDate") or item.get("passDate")
        issue_date = raw_issue[:10] if raw_issue else "N/A"
        
        # Expiry Logic
        raw_expiry = item.get("expirationDate")
        if not raw_expiry and "certificationStatus" in item:
            raw_expiry = item["certificationStatus"].get("expirationDate")

        if raw_expiry:
            expiry_dt = datetime.strptime(raw_expiry[:10], "%Y-%m-%d").date()
            renewal_open = expiry_dt - timedelta(days=180)
            today = datetime.now().date()
            
            status = "🟢 ACTIVE"
            if today >= expiry_dt: status = "🔴 EXPIRED"
            elif today >= renewal_open: status = "🟡 RENEW NOW"
            
            exp_display, ren_display = str(expiry_dt), str(renewal_open)
        else:
            exp_display, ren_display, status = "Lifetime", "N/A", "🟢 ACTIVE"

        cert_list.append({
            "Credential": name,
            "Issue Date": issue_date,
            "Expiry Date": exp_display,
            "Renewal Window Opens": ren_display,
            "Status": status
        })

    # --- DISPLAY ---
    if cert_list:
        df = pd.DataFrame(cert_list).drop_duplicates(subset=['Credential'])
        
        def style_status(val):
            if val == "🟡 RENEW NOW": return 'background-color: #fff3cd; color: #856404; font-weight: bold'
            if val == "🔴 EXPIRED": return 'background-color: #f8d7da; color: #721c24'
            if val == "🟢 ACTIVE": return 'background-color: #d4edda; color: #155724'
            return ''

        st.dataframe(df.style.applymap(style_status, subset=['Status']), use_container_width=True, hide_index=True)
else:
    st.error("Error: Could not access Microsoft Learn data.")
