import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIG ---
TRANSCRIPT_ID = "dz336sng53l39pp"
URL = f"https://learn.microsoft.com/api/profiles/transcript/share/{TRANSCRIPT_ID}"

st.set_page_config(page_title="MS Cert Dashboard", layout="wide")
st.title("🎓 Microsoft Learning & Certification Tracker")

def fetch_data():
    try:
        response = requests.get(URL)
        return response.json() if response.status_code == 200 else None
    except: return None

data = fetch_data()

if data:
    # 1. SUMMARY STATS
    col1, col2, col3 = st.columns(3)
    col1.metric("Modules Completed", data.get("totalModulesCompleted", 0))
    col2.metric("Learning Paths", data.get("totalLearningPathsCompleted", 0))
    col3.metric("Study Hours", round(data.get("totalTrainingMinutes", 0) / 60, 1))

    # 2. RENEWAL TRACKER
    st.subheader("🛡️ Certification & Exam Renewal Tracker")
    
    # We pull from ALL possible lists Microsoft provides
    c_data = data.get("certificationData", {})
    list_a = c_data.get("activeCertifications", [])
    list_b = data.get("examData", {}).get("passedExams", [])
    list_c = data.get("appliedSkillsData", {}).get("appliedSkills", [])
    
    raw_list = list_a + list_b + list_c
    final_certs = []

    for item in raw_list:
        # Get Name
        name = item.get("certificationName") or item.get("examName") or item.get("title") or "Unknown"
        
        # Get Issue Date
        raw_issue = item.get("issueDate") or item.get("passDate") or item.get("achievementDate")
        issue_date = raw_issue[:10] if raw_issue else "N/A"
        
        # Get Expiry Logic
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

        final_certs.append({
            "Certification/Exam": name,
            "Issue Date": issue_date,
            "Expiry Date": exp_display,
            "Renewal Opens": ren_display,
            "Status": status
        })

    if final_certs:
        df = pd.DataFrame(final_certs).drop_duplicates(subset=['Certification/Exam'])
        
        def style_status(val):
            if val == "🟡 RENEW NOW": return 'background-color: #fff3cd; color: #856404; font-weight: bold'
            if val == "🔴 EXPIRED": return 'background-color: #f8d7da; color: #721c24'
            if val == "🟢 ACTIVE": return 'background-color: #d4edda; color: #155724'
            return ''

        st.dataframe(df.style.applymap(style_status, subset=['Status']), use_container_width=True, hide_index=True)
    else:
        st.warning("No Certifications or Exams found. Please go to your Microsoft Learn Transcript settings and ensure 'Certifications' and 'Exams' are checked in the 'Include in share' section.")

    # 3. RECENT TRAINING
    st.subheader("📚 Recent Training")
    for m in data.get("modulesCompleted", [])[:5]:
        st.write(f"- **{m['title']}** ({m['completedOn'][:10]})")
else:
    st.error("Failed to connect to Microsoft Learn API.")
