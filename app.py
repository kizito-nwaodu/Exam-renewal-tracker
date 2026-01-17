import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIG ---
TRANSCRIPT_ID = "dz336sng53l39pp"
URL = f"https://learn.microsoft.com/api/profiles/transcript/share/{TRANSCRIPT_ID}"

st.set_page_config(page_title="MS Cert Tracker", page_icon="🎓", layout="wide")
st.title("🎓 Microsoft Certification Tracker")

def fetch_data():
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Network Error: {e}")
        return None

def get_best_name(obj):
    """Deep search for the title of the achievement."""
    # List of possible keys Microsoft uses for titles
    keys = ["certificationName", "title", "examName", "appliedSkillName", "name", "courseName"]
    for key in keys:
        if obj.get(key):
            return obj.get(key)
    return "Unnamed Achievement"

data = fetch_data()

if data:
    cert_list = []
    
    # Extracting all possible sections from the JSON
    cert_data = data.get("certificationData", {})
    active_certs = cert_data.get("activeCertifications", [])
    applied_skills = data.get("appliedSkillsData", {}).get("appliedSkills", [])
    exams = data.get("examData", {}).get("passedExams", []) # Adding passed exams
    
    # Process everything
    all_items = active_certs + applied_skills + exams

    for item in all_items:
        name = get_best_name(item)
        
        # Handle Dates
        raw_issue = item.get("issueDate") or item.get("achievementDate") or item.get("passDate")
        issue_date = raw_issue[:10] if raw_issue else "N/A"
        
        expiry_date_str = item.get("expirationDate")
        
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str[:10], "%Y-%m-%d").date()
                renewal_open = expiry_date - timedelta(days=180)
                days_left = (expiry_date - datetime.now().date()).days
                
                if days_left < 0:
                    status = "🔴 Expired"
                elif datetime.now().date() >= renewal_open:
                    status = "🟡 RENEW NOW"
                else:
                    status = "🟢 Active"
            except:
                expiry_date = "N/A"
                renewal_open = "N/A"
                status = "❓ Unknown"
        else:
            # Fundamentals, Exams, and Applied Skills don't expire
            expiry_date = "Lifetime"
            renewal_open = "N/A"
            status = "🟢 Active"

        cert_list.append({
            "Certification": name,
            "Issue Date": issue_date,
            "Expiry Date": expiry_date,
            "Renewal Opens": renewal_open,
            "Status": status
        })

    if cert_list:
        df = pd.DataFrame(cert_list)
        # Drop duplicates based on Name
        df = df.drop_duplicates(subset=['Certification'])
        
        # Styling
        def color_status(val):
            if "RENEW" in val: return 'background-color: #fff3cd; color: #856404; font-weight: bold'
            if "Expired" in val: return 'background-color: #f8d7da; color: #721c24'
            if "Active" in val: return 'background-color: #d4edda; color: #155724'
            return ''

        st.dataframe(
            df.style.applymap(color_status, subset=['Status']),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Data found, but no certifications were detected. Check your Transcript settings.")
else:
    st.error("Could not reach Microsoft Learn API. Verify your Transcript ID.")
