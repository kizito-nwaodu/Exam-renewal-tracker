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
        st.error(f"Error: {e}")
        return None

data = fetch_data()

if data:
    # Microsoft often nests these under 'certificationData' -> 'activeCertifications'
    cert_data = data.get("certificationData", {})
    certs = cert_data.get("activeCertifications", [])
    
    cert_list = []
    
    for c in certs:
        # Try to find the title in different possible keys
        name = c.get("certificationName") or c.get("title") or "Unnamed Achievement"
        
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
        
        # Sort so that those expiring soonest are at the top
        # We handle 'Lifetime' strings so they don't break sorting
        df['SortDate'] = df['Expiry Date'].apply(lambda x: x if isinstance(x, datetime) or hasattr(x, 'year') else datetime(2099, 1, 1).date())
        df = df.sort_values(by="SortDate").drop(columns=['SortDate'])

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
        
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.warning("No certifications found. Please check if your transcript is shared correctly.")
else:
    st.error("Access Denied. Please ensure your Transcript is 'Public' in Microsoft Learn settings.")
