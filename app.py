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
        st.error(f"Error fetching data: {e}")
        return None

data = fetch_data()

if data:
    cert_list = []
    
    # 1. PULL ROLE-BASED & FUNDAMENTALS
    active_certs = data.get("certificationData", {}).get("activeCertifications", [])
    # 2. PULL APPLIED SKILLS
    applied_skills = data.get("appliedSkillsData", {}).get("appliedSkills", [])
    
    # Combine lists to process them all
    all_achievements = active_certs + applied_skills

    for c in all_achievements:
        # Microsoft uses different keys for different achievement types
        name = (c.get("certificationName") or 
                c.get("title") or 
                c.get("appliedSkillName") or 
                "Unknown Achievement")
        
        # Date Handling
        raw_issue = c.get("issueDate") or c.get("achievementDate")
        issue_date = raw_issue[:10] if raw_issue else "N/A"
        
        expiry_date_str = c.get("expirationDate")
        
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
                status = "❓ Check Learn"
        else:
            # Fundamentals & Applied Skills usually don't expire
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
        
        # Remove duplicates (sometimes MS lists things in two places)
        df = df.drop_duplicates(subset=['Certification'])

        # Color Formatting
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
        
        st.success(f"Successfully tracked {len(df)} achievements!")
    else:
        st.warning("No achievements found. Is your transcript definitely public?")
else:
    st.error("Access Denied. Ensure your Transcript Share Link is valid.")
