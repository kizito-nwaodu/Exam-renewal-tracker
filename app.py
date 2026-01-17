import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIG ---
TRANSCRIPT_ID = "dz336sng53l39pp"
URL = f"https://learn.microsoft.com/api/profiles/transcript/share/{TRANSCRIPT_ID}"

st.set_page_config(page_title="MS Cert Dashboard", layout="wide")

# --- DATA FETCHING ---
def fetch_data():
    try:
        response = requests.get(URL)
        return response.json() if response.status_code == 200 else None
    except: return None

data = fetch_data()

# --- UI ---
st.title("🎓 Microsoft Learning & Certification Tracker")

if data:
    # 1. SUMMARY STATS
    col1, col2, col3 = st.columns(3)
    col1.metric("Modules Completed", data.get("totalModulesCompleted", 0))
    col2.metric("Learning Paths", data.get("totalLearningPathsCompleted", 0))
    col3.metric("Study Hours", round(data.get("totalTrainingMinutes", 0) / 60, 1))

    # 2. RENEWAL TRACKER LOGIC
    st.subheader("🛡️ Certification Renewal Tracker")
    
    cert_list = []
    # Grab all active certifications
    active_certs = data.get("certificationData", {}).get("activeCertifications", [])
    
    for c in active_certs:
        name = c.get("certificationName") or c.get("title") or "Unknown Cert"
        
        # Get Issue Date
        raw_issue = c.get("issueDate") or c.get("achievementDate")
        issue_date = raw_issue[:10] if raw_issue else "N/A"
        
        # Get Expiration Date (Deep Search)
        raw_expiry = c.get("expirationDate")
        if not raw_expiry and "certificationStatus" in c:
            raw_expiry = c["certificationStatus"].get("expirationDate")
        
        if raw_expiry:
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
        else:
            # For Fundamentals
            exp_display = "LIFETIME"
            ren_display = "N/A"
            status = "🟢 ACTIVE"

        cert_list.append({
            "Certification": name,
            "Issue Date": issue_date,
            "Expiry Date": exp_display,
            "Renewal Window Opens": ren_display,
            "Status": status
        })

    if cert_list:
        df = pd.DataFrame(cert_list).drop_duplicates(subset=['Certification'])
        
        # Styling function
        def style_status(val):
            if val == "🟡 RENEWAL OPEN": return 'background-color: #fff3cd; color: #856404; font-weight: bold'
            if val == "🔴 EXPIRED": return 'background-color: #f8d7da; color: #721c24'
            if val == "🟢 ACTIVE": return 'background-color: #d4edda; color: #155724'
            return ''

        st.dataframe(
            df.style.applymap(style_status, subset=['Status']),
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.info("No certifications found. Please check your transcript sharing settings.")

    # 3. RECENT ACTIVITY
    st.subheader("📚 Recent Training")
    modules = data.get("modulesCompleted", [])[:5]
    for m in modules:
        st.write(f"- **{m['title']}** (Completed: {m['completedOn'][:10]})")

else:
    st.error("Could not fetch data. Verify your Transcript ID.")
