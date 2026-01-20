import streamlit as st
import json
import os
from db531 import load_user_schedule, load_progress, save_progress

# --- CONFIG ---
st.set_page_config(page_title="5/3/1 Training", layout="centered")

# Custom CSS for the Green "Complete" button
st.markdown("""
    <style>
    div.stButton > button[kind="primary"] {
        background-color: #28a745;
        color: white;
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if 'page' not in st.session_state:
    st.session_state['page'] = 'login'

# --- DIALOG POPUP ---
@st.dialog("Workout Finished")
def completion_dialog(day_label, username, day_key, week_num):
    st.write(f"### Finalize {day_label}?")
    st.write("Confirm you have finished all sets. This will lock today's log.")
    
    col1, col2 = st.columns(2)
    if col1.button("Confirm", type="primary", use_container_width=True):
        progress = load_progress(username)
        progress[f"day_done_w{week_num}_d{day_key}"] = True
        save_progress(username, progress)
        st.session_state['page'] = 'selection'
        st.rerun()
    
    if col2.button("Cancel", use_container_width=True):
        st.rerun()

# ==========================================
# PAGE 1: LOGIN
# ==========================================
if st.session_state['page'] == 'login':
    st.title("🏋️ 5/3/1 Login")
    u = st.text_input("Username").lower().strip()
    p = st.text_input("Password", type="password")
    
    if st.button("Enter", type="primary"):
        schedule = load_user_schedule(u)
        if schedule and schedule.get('password') == p:
            st.session_state['username'] = u
            st.session_state['page'] = 'selection'
            st.rerun()
        else:
            st.error("Invalid Username or Password")

# ==========================================
# PAGE 2: SELECTION
# ==========================================
elif st.session_state['page'] == 'selection':
    username = st.session_state['username']
    schedule = load_user_schedule(username)
    
    st.title("Main Menu")
    st.write(f"Logged in: **{username.capitalize()}**")
    
    # Dropdown 1: Week
    sel_week = st.selectbox("Select Training Week", ["1", "2", "3", "4"])
    
    # Dropdown 2: Day (Calculated dynamically from the schedule)
    day_map = {}
    for d in ["1", "2", "3", "4"]:
        # Find the main lift for the label
        main_lift = next((ex['exercise'] for ex in schedule['weeks'][sel_week].get(d, []) if ex['tags'] == 'main'), "Supplemental")
        label = f"Day {d}: {main_lift}"
        day_map[label] = d

    sel_day_label = st.selectbox("Select Workout Day", options=list(day_map.keys()))
    sel_day_key = day_map[sel_day_label]

    if st.button("Start Workout", type="primary"):
        st.session_state['sel_week'] = sel_week
        st.session_state['sel_day_key'] = sel_day_key
        st.session_state['sel_day_label'] = sel_day_label
        st.session_state['page'] = 'workout'
        st.rerun()
        
    if st.button("Logout"):
        st.session_state['page'] = 'login'
        st.rerun()

# ==========================================
# PAGE 3: WORKOUT
# ==========================================
elif st.session_state['page'] == 'workout':
    username = st.session_state['username']
    week = st.session_state['sel_week']
    day_key = st.session_state['sel_day_key']
    day_label = st.session_state['sel_day_label']
    
    schedule = load_user_schedule(username)
    progress = load_progress(username)
    
    # Check if this day was previously locked
    is_day_done = progress.get(f"day_done_w{week}_d{day_key}", False)

    # HEADER: Context on left, Menu on right
    header_col, menu_col = st.columns([3, 1])
    with header_col:
        st.caption(f"{username.upper()} • WEEK {week}")
        st.subheader(day_label)
    with menu_col:
        if st.button("Menu ☰"):
            st.session_state['page'] = 'selection'
            st.rerun()

    st.divider()

    # List Exercises
    exercises = schedule['weeks'][week].get(day_key, [])
    day_exercise_keys = []

    for ex_idx, ex in enumerate(exercises):
        # Create unique key for progress tracking
        ex_key = f"{username}_w{week}_d{day_key}_ex{ex_idx}"
        day_exercise_keys.append(ex_key)
        
        # Exercise Display
        st.markdown(f"**:blue[{ex['exercise'].upper()}]**")
        
        sets_text = " • ".join([f"{s['reps']}x{s['weight']}" for s in ex['sets']])
        # Use a div with a font-size of 1.5rem (roughly Header 3 size) but no bold
        st.markdown(f'<div style="font-size: 1.5rem;">{sets_text}</div>', unsafe_allow_html=True)
        
        # Checkbox
        checked = st.checkbox("DONE", value=progress.get(ex_key, False), key=ex_key, disabled=is_day_done)
        
        if checked != progress.get(ex_key, False):
            progress[ex_key] = checked
            save_progress(username, progress)
            st.rerun()
        
        st.divider()

    # FOOTER: Finalize Button
    all_checked = all(progress.get(k, False) for k in day_exercise_keys)
    
    if not is_day_done:
        # Button turns green only when all boxes are checked
        btn_style = "primary" if all_checked else "secondary"
        if st.button("COMPLETE WORKOUT", type=btn_style):
            if all_checked:
                completion_dialog(day_label, username, day_key, week)
            else:
                st.warning("Finish all exercises before completing.")
    else:
        st.success("Workout Logged for today.")