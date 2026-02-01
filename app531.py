import streamlit as st
import json
from db531 import load_progress, save_progress

# --- 1. UI CONFIG & SKIN ---
st.set_page_config(page_title="5/3/1 Training", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="st-"] {
        font-size: 1.2rem !important;
    }
    [data-testid="stCheckbox"] {
        transform: scale(1.8);
        margin-left: 15px;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    .stButton > button {
        height: 4em !important;
        width: 100% !important;
        font-size: 1.2rem !important;
    }
    div.stButton > button[kind="primary"] {
        background-color: #28a745;
        color: white;
        border-radius: 10px;
        font-weight: bold;
    }
    hr {
        margin-top: 2rem !important;
        margin-bottom: 2rem !important;
        border-top: 2px solid #444 !important;
    }
    </style>
""", unsafe_allow_html=True)

if 'page' not in st.session_state:
    st.session_state['page'] = 'login'

# --- 2. DIALOGS ---
@st.dialog("Workout Finished")
def completion_dialog(day_label, username, day_key, week_num):
    st.write(f"### Finalize {day_label}?")
    st.write("Confirm you have finished all sets.")
    col1, col2 = st.columns(2)
    if col1.button("Confirm", type="primary"):
        progress = load_progress(username)
        progress[f"day_done_w{week_num}_d{day_key}"] = True
        save_progress(username, progress)
        st.session_state['page'] = 'selection'
        st.rerun()
    if col2.button("Cancel"):
        st.rerun()

# --- 3. PAGE LOGIC ---

# PAGE 1: LOGIN
if st.session_state['page'] == 'login':
    st.title("🏋️ 5/3/1 Login")
    u = st.text_input("Username").lower().strip()
    p = st.text_input("Password", type="password")
    
    if st.button("Enter", type="primary"):
        try:
            with open("schedule_fsalinas.json", "r") as f:
                full_data = json.load(f)
            
            if u == full_data.get('username') and p == full_data.get('password'):
                st.session_state['username'] = u
                st.session_state['page'] = 'selection'
                st.rerun()
            else:
                st.error("Invalid Username or Password")
        except FileNotFoundError:
            st.error("Error: schedule_fsalinas.json not found in folder.")
        except json.JSONDecodeError:
            st.error("Error: schedule_fsalinas.json has formatting errors (check quotes).")

# PAGE 2: SELECTION
elif st.session_state['page'] == 'selection':
    with open("schedule_fsalinas.json", "r") as f:
        schedule = json.load(f)
        
    username = st.session_state['username']
    st.title("Main Menu")
    
    sel_week = st.selectbox("Select Training Week", ["1", "2", "3", "4"])
    
    # Extract main lifts for the labels
    day_options = ["1", "2", "3", "4"]
    day_map = {}
    for d in day_options:
        day_exercises = schedule['weeks'][sel_week].get(d, [])
        main_lift = next((ex['exercise'] for ex in day_exercises if ex.get('tags') == 'main'), "Supplemental")
        label = f"Day {d}: {main_lift}"
        day_map[label] = d
    
    sel_day_label = st.selectbox("Select Workout Day", options=list(day_map.keys()))
    sel_day_key = day_map[sel_day_label]
    
    if st.button("Start Workout", type="primary"):
        st.session_state.update({
            'sel_week': sel_week, 
            'sel_day_key': sel_day_key, 
            'sel_day_label': sel_day_label, 
            'page': 'workout'
        })
        st.rerun()
    
    if st.button("Logout"):
        st.session_state['page'] = 'login'
        st.rerun()

# PAGE 3: WORKOUT
elif st.session_state['page'] == 'workout':
    username = st.session_state['username']
    week = st.session_state['sel_week']
    day_key = st.session_state['sel_day_key']
    day_label = st.session_state['sel_day_label']
    
    with open("schedule_fsalinas.json", "r") as f:
        schedule = json.load(f)
        
    progress = load_progress(username)
    is_day_done = progress.get(f"day_done_w{week}_d{day_key}", False)

    c1, c2 = st.columns([3, 1])
    c1.subheader(day_label)
    if c2.button("Menu ☰"): 
        st.session_state['page'] = 'selection'
        st.rerun()

    st.divider()
    exercises = schedule['weeks'][week].get(day_key, [])
    day_keys = []

    for idx, ex in enumerate(exercises):
        ex_key = f"{username}_w{week}_d{day_key}_ex{idx}"
        day_keys.append(ex_key)
        
        st.markdown(f"**:blue[{ex['exercise'].upper()}]**")
        sets_text = " • ".join([f"{s['reps']}x{s['weight']}" for s in ex['sets']])
        st.markdown(f'<div style="font-size: 1.6rem; margin-bottom: 10px;">{sets_text}</div>', unsafe_allow_html=True)
        
        # Checkbox logic with instant Cloud Save to Google Sheets
        is_checked = progress.get(ex_key, False)
        checked = st.checkbox("DONE", value=is_checked, key=ex_key, disabled=is_day_done)
        
        if checked != is_checked:
            progress[ex_key] = checked
            save_progress(username, progress)
            st.rerun()
        st.divider()

    if not is_day_done:
        all_c = all(progress.get(k, False) for k in day_keys)
        btn_style = "primary" if all_c else "secondary"
        if st.button("COMPLETE WORKOUT", type=btn_style):
            if all_c: 
                completion_dialog(day_label, username, day_key, week)
            else: 
                st.warning("Finish all exercises.")