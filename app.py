import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIG ---
TRANSCRIPT_ID = "dz336sng53l39pp"
URL = f"https://learn.microsoft.com/api/profiles/transcript/share/{TRANSCRIPT_ID}"

st.set_page_config(page_title="MS Cert Tracker", page_icon="🎓", layout="wide")
st.title("🎓 Microsoft Certification Tracker")

# Debugging Tool
show_raw = st.sidebar.checkbox("Show Raw Data (Debug)")

def fetch_data():
    try:
        response = requests.get(URL)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

data = fetch_data()

if show_raw and data:
    st.write(data)

if data:
    cert_list = []
    
    # MS Learn JSON structure usually separates Certs and Skills
    certs_data = data.get("certificationData", {})
    active_certs = certs_data.get("activeCertifications", [])
    skills_data = data.get("appliedSkillsData", {})
    skills = skills_data.get("appliedSkills", []) or skills_data.get("appliedSkillsCredentials", [])
    exams = data.get("examData", {}).get("passedExams", [])
    
    all_items = active_certs + skills + exams

    for item in all_items:
        # Get Name
        name = item.get("certificationName") or item.get("title") or item.get("examName") or "Unknown"
        
        # Get Issue Date
        raw_issue = item.get("issueDate") or item.get("achievementDate") or item.get("passDate")
        issue_date = raw_issue[:10] if raw_issue else "N/A"
        
        # Get Expiration Date (Looking in root and sub-objects)
        raw_expiry = item.get("expirationDate")
        if not raw_expiry and "certificationStatus" in item:
            raw_expiry = item["certificationStatus"].get("expirationDate")

        # Process Logic
        if raw_expiry:
            try:
                expiry_dt = datetime.strptime(raw_expiry[:10], "%Y-%m-%d").date()
                renewal_open = expiry_dt - timedelta(days=180)
                today = datetime.now().date()
                
                if today >= expiry_dt:
                    status = "🔴 EXPIRED"
                elif today >= renewal_open:
                    status = "🟡 RENEWAL OPEN"
                else:
                    status = "🟢 ACTIVE"
                
                exp_display = str(expiry_dt)
                ren_display = str(renewal_open)
            except:
                exp_display, ren_display, status = "N/A", "N/A", "❓ Error"
        else:
            exp_display, ren_display, status = "LIFETIME", "N/A", "🟢 ACTIVE"

        cert_list.append({
            "Certification": name,
            "Issue Date": issue_date,
            "Expiry Date": exp_display,
            "Renewal Window Opens": ren_display,
            "Status": status
        })

    if cert_list:
        df = pd.DataFrame(cert_list).drop_duplicates(subset=['Certification'])
        
        # UI Styling
        def style_table(val):
            color = ''
            if val == "🟡 RENEWAL OPEN": color = 'background-color: #fff3cd; font-weight: bold'
            if val == "🔴 EXPIRED": color = 'background-color: #f8d7da'
            if val == "🟢 ACTIVE": color = 'background-color: #d4edda'
            return f'color: black; {color}'

        st.dataframe(df.style.applymap(style_table, subset=['Status']), use_container_width=True, hide_index=True)
    else:
        st.info("No certifications found. Ensure your transcript is shared publicly.")
