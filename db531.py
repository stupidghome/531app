import json
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# =================================================================
# GOOGLE SHEETS CONNECTION
# =================================================================

def get_gspread_client():
    """Authenticates using Streamlit Secrets and returns the gspread client."""
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    # Reads the TOML secrets you just saved
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    return gspread.authorize(creds)

def get_worksheet(sheet_name):
    """Opens the gym531_fs workbook and returns the requested tab."""
    client = get_gspread_client()
    sh = client.open("gym531_fs")
    return sh.worksheet(sheet_name)

# =================================================================
# DATABASE & FILE I/O LAYER (NOW VIA SHEETS)
# =================================================================

def load_user_schedule(username):
    """Loads the schedule from the 'schedule' tab."""
    try:
        ws = get_worksheet("schedule")
        records = ws.get_all_records()
        for row in records:
            if str(row.get('username')).lower() == username.lower():
                return json.loads(row.get('data'))
        return None
    except Exception as e:
        st.error(f"Error loading schedule: {e}")
        return None

def load_progress(username):
    """Loads progress from the 'progress' tab."""
    try:
        ws = get_worksheet("progress")
        records = ws.get_all_records()
        for row in records:
            if str(row.get('username')).lower() == username.lower():
                # Google Sheets might return a string or dict; ensure it's a dict
                data = row.get('data')
                return json.loads(data) if isinstance(data, str) else data
        return {}
    except:
        return {}

def save_progress(username, progress_data):
    """Saves progress data back to the 'progress' tab."""
    try:
        ws = get_worksheet("progress")
        # Look for the username in Column A
        cell = ws.find(username.lower())
        
        json_string = json.dumps(progress_data)
        
        if cell:
            # Update existing row (Column B is index 2)
            ws.update_cell(cell.row, 2, json_string)
        else:
            # Create new row: [username, data]
            ws.append_row([username.lower(), json_string])
    except Exception as e:
        st.error(f"Failed to save to Cloud: {e}")
