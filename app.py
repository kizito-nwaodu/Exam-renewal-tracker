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

def get_best_name(obj):
    keys = ["certificationName", "title", "examName", "appliedSkillName", "name"]
    for key in keys:
        if obj.get(key): return obj.get(key)
    return "Unknown Achievement"

data = fetch_data()

if data:
    cert_list = []
    # Pulling from all possible data buckets
    active_certs = data.get("certificationData", {}).get("activeCertifications", [])
    applied_skills = data.get("appliedSkillsData", {}).get("appliedSkills", [])
    exams = data.get("examData", {}).get("passedExams", [])
    
    all_items = active_certs + applied_skills + exams

    for item in all_items:
        name = get_best_name(item)
        
        # 1. FIND THE ISSUE DATE
        # MS uses achievementDate for certs and passDate for exams
        raw_issue = item.get("issueDate") or item.get("achievementDate") or item.get("passDate")
        issue_date = raw_issue[:10] if raw_issue else "N/A"
        
        # 2. FIND THE EXPIRY DATE
        # Look in the main object OR inside a 'certificationStatus' sub-object
        raw_expiry = item.get("expirationDate")
        if not raw_expiry and item.get("certificationStatus"):
            raw_expiry = item.get("certificationStatus", {}).get("expirationDate")
            
        # 3. CALCULATE STATUS AND RENEWAL
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
                
                display_expiry = expiry_dt
                display_renewal = renewal_open
            except:
                display_expiry = "N/A"
                display_renewal = "N/A"
                status = "❓ Unknown"
        else:
            # If no expiry is found, it's a Lifetime cert (like Fundamentals)
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
        st.warning("No data found.")
else:
    st.error("Could not fetch data.")
