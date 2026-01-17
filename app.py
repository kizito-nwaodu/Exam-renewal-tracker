import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIG ---
TRANSCRIPT_ID = "dz336sng53l39pp"
URL = f"https://learn.microsoft.com/api/profiles/transcript/share/{TRANSCRIPT_ID}"

st.set_page_config(page_title="MS Cert Tracker", page_icon="🎓")
st.title("🎓 Microsoft Certification Tracker")

def fetch_data():
    try:
        response = requests.get(URL)
        return response.json()
    except Exception as e:
        st.error(f"Error connecting to Microsoft: {e}")
        return None

data = fetch_data()

if data:
    certs = data.get("certificationData", {}).get("activeCertifications", [])
    cert_list = []
    
    for c in certs:
        name = c.get("title", "Unknown Certification")
        
        # FIX: Check if issueDate exists before slicing
        raw_issue_date = c.get("issueDate")
        issue_date = raw_issue_date[:10] if raw_issue_date else "N/A"
        
        # FIX: Check if expirationDate exists before processing
        expiry_date_str = c.get("expirationDate")
        
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str[:10], "%Y-%m-%d").date()
                renewal_open = expiry_date - timedelta(days=180)
                days_until_expiry = (expiry_date - datetime.now().date()).days
                
                if days_until_expiry < 0:
                    status = "🔴 Expired"
                elif datetime.now().date() >= renewal_open:
                    status = "🟡 RENEW NOW"
                else:
                    status = "🟢 Active"
            except:
                expiry_date = "Invalid Date"
                renewal_open = "N/A"
                status = "❓ Check Learn"
        else:
            # This handles Fundamentals (AZ-900, etc.) which don't expire
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
        
        # Simple coloring logic
        def color_status(val):
            if "RENEW" in val: return 'background-color: #fff3cd' # Yellow
            if "Expired" in val: return 'background-color: #f8d7da' # Red
            if "Active" in val: return 'background-color: #d4edda' # Green
            return ''

        st.table(df.style.applymap(color_status, subset=['Status']))
    else:
        st.warning("No active certifications found in this transcript.")

else:
    st.error("Could not fetch data. Please verify your Transcript ID and ensure it is set to 'Public'.")
