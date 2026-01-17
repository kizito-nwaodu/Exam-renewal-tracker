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
        return response.json() if response.status_code == 200 else None
    except:
        return None

def find_key_recursive(obj, target_key):
    """Searches for a key anywhere inside a nested dictionary or list."""
    if isinstance(obj, dict):
        if target_key in obj:
            return obj[target_key]
        for key, value in obj.items():
            result = find_key_recursive(value, target_key)
            if result: return result
    elif isinstance(obj, list):
        for item in obj:
            result = find_key_recursive(item, target_key)
            if result: return result
    return None

data = fetch_data()

if data:
    cert_list = []
    
    # Sections to scan
    active_certs = data.get("certificationData", {}).get("activeCertifications", [])
    applied_skills = data.get("appliedSkillsData", {}).get("appliedSkills", [])
    exams = data.get("examData", {}).get("passedExams", [])
    
    all_items = active_certs + applied_skills + exams

    for item in all_items:
        # 1. GET NAME
        name = (item.get("certificationName") or item.get("title") or 
                item.get("examName") or item.get("name") or "Achievement")
        
        # 2. GET ISSUE DATE
        # We search the item specifically for any variation of 'issue' or 'achievement' date
        raw_issue = (item.get("issueDate") or item.get("achievementDate") or 
                     item.get("passDate") or find_key_recursive(item, "achievementDate"))
        issue_date = raw_issue[:10] if raw_issue else "N/A"
        
        # 3. GET EXPIRATION DATE
        # We search the item specifically for 'expirationDate'
        raw_expiry = item.get("expirationDate") or find_key_recursive(item, "expirationDate")
        
        if raw_expiry:
            try:
                expiry_dt = datetime.strptime(raw_expiry[:10], "%Y-%m-%d").date()
                renewal_open = expiry_dt - timedelta(days=180)
                today = datetime.now().date()
                
                if today >= expiry_dt:
                    status = "🔴 Expired"
                elif today >= renewal_open:
                    status = "🟡 RENEW NOW"
                else:
                    status = "🟢 Active"
                
                display_expiry = str(expiry_dt)
                display_renewal = str(renewal_open)
            except:
                display_expiry = "N/A"
                display_renewal = "N/A"
                status = "❓ Unknown"
        else:
            # Fundamentals & Exams
            display_expiry = "Lifetime"
            display_renewal = "N/A"
            status = "🟢 Active"

        cert_list.append({
            "Certification": name,
            "Issue Date": issue_date,
            "Expiry Date": display_expiry,
            "Renewal Opens": display_renewal,
            "Status": status
        })

    if cert_list:
        df = pd.DataFrame(cert_list).drop_duplicates(subset=['Certification'])
        
        # Custom coloring for the table
        def style_rows(row):
            if "RENEW" in row.Status: return ['background-color: #fff3cd'] * len(row)
            if "Expired" in row.Status: return ['background-color: #f8d7da'] * len(row)
            return [''] * len(row)

        st.dataframe(df.style.apply(style_rows, axis=1), use_container_width=True, hide_index=True)
        st.success(f"Found {len(df)} entries. Use the table above to track your renewals.")
    else:
        st.warning("No data found.")
else:
    st.error("Could not fetch data. Check your connection or Transcript ID.")
