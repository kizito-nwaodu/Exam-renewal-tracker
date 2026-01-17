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
    except:
        return None

data = fetch_data()

if data:
    # Pulling from the specific path in the MS Learn JSON
    certs = data.get("certificationData", {}).get("activeCertifications", [])
    
    cert_list = []
    for c in certs:
        name = c.get("title")
        issue_date = c.get("issueDate")[:10] # Formatting date
        expiry_date_str = c.get("expirationDate")
        
        if expiry_date_str:
            expiry_date = datetime.strptime(expiry_date_str[:10], "%Y-%m-%d").date()
            # Renewal opens 180 days (6 months) before expiry
            renewal_open = expiry_date - timedelta(days=180)
            days_until_expiry = (expiry_date - datetime.now().date()).days
            
            # Logic for status
            if days_until_expiry < 0:
                status = "🔴 Expired"
            elif datetime.now().date() >= renewal_open:
                status = "🟡 RENEW NOW (Open)"
            else:
                status = "🟢 Active"
        else:
            expiry_date = "N/A (Fundamentals)"
            renewal_open = "N/A"
            status = "🟢 Lifetime"

        cert_list.append({
            "Certification": name,
            "Expiry Date": expiry_date,
            "Renewal Opens": renewal_open,
            "Status": status
        })

    # Create Table
    df = pd.DataFrame(cert_list)
    
    # CSS to color the rows
    def color_status(val):
        if "RENEW" in val: return 'background-color: #ffebcc'
        if "Expired" in val: return 'background-color: #ffcccc'
        if "Active" in val: return 'background-color: #e6ffed'
        return ''

    st.table(df.style.applymap(color_status, subset=['Status']))
    
    st.info("💡 Tip: Set up a GitHub Action to run this script weekly and email you if Status is 'RENEW NOW'.")

else:
    st.error("Failed to load data. Ensure your Transcript is set to 'Public' in Microsoft Learn.")
