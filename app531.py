import streamlit as st
import json
from db531 import load_user_schedule, load_progress, save_progress

# --- 1. UI CONFIG & SKIN ---
st.set_page_config(page_title="5/3/1 Training", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 1.2rem !important; }
    [data-testid="stCheckbox"] { transform: scale(1.8); margin-left: 15px; margin-bottom: 20px; }
    .stButton > button { height: 4em !important; width: 100% !important; font-size: 1.2rem !important; }
    div.stButton > button[kind="primary"] { background-color: #28a745; color: white; border-radius: 10px; font-weight: bold; }
    hr { margin-top: 2rem !important; margin-bottom: 2rem !important; border-top: 2px solid #444 !important; }
    </style>
""", unsafe_allow_html=True)

if 'page' not in st.session_state:
    st.session_state['page'] = 'login'

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

# PAGE 1: LOGIN
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

# PAGE 2: SELECTION
elif st.session_state['page'] == 'selection':
    username = st.session_state['username']
    schedule = load_user_schedule(username)
    if not schedule:
        st.error("Schedule not found in Google Sheets.")
        if st.button("Logout"): st.session_state['page'] = 'login'; st.rerun()
    else:
        st.title("Main Menu")
        sel_week = st.selectbox("Select Training Week", ["1", "2", "3", "4"])
        day_map = {f"Day {d}: {next((ex['exercise'] for ex in schedule['weeks'][sel_week].get(d, []) if ex['tags'] == 'main'), 'Supplemental')}": d for d in ["1", "2", "3", "4"]}
        
        sel_day_label = st.selectbox("Select Workout Day", options=list(day_map.keys()))
        sel_day_key = day_map[sel_day_label]
        
        if st.button("Start Workout", type="primary"):
            st.session_state.update({'sel_week': sel_week, 'sel_day_key': sel_day_key, 'sel_day_label': sel_day_label, 'page': 'workout'})
            st.rerun()

# PAGE 3: WORKOUT
elif st.session_state['page'] == 'workout':
    username = st.session_state['username']
    week, day_key, day_label = st.session_state['sel_week'], st.session_state['sel_day_key'], st.session_state['sel_day_label']
    schedule = load_user_schedule(username)
    progress = load_progress(username)
    is_day_done = progress.get(f"day_done_w{week}_d{day_key}", False)

    c1, c2 = st.columns([3, 1])
    c1.subheader(day_label)
    if c2.button("Menu ☰"): st.session_state['page'] = 'selection'; st.rerun()

    st.divider()
    exercises = schedule['weeks'][week].get(day_key, [])
    day_keys = []

    for idx, ex in enumerate(exercises):
        ex_key = f"{username}_w{week}_d{day_key}_ex{idx}"
        day_keys.append(ex_key)
        st.markdown(f"**:blue[{ex['exercise'].upper()}]**")
        sets = " • ".join([f"{s['reps']}x{s['weight']}" for s in ex['sets']])
        st.markdown(f'<div style="font-size: 1.6rem; margin-bottom: 10px;">{sets}</div>', unsafe_allow_html=True)
        
        # INSTANT CLOUD SAVE
        if st.checkbox("DONE", value=progress.get(ex_key, False), key=ex_key, disabled=is_day_done):
            if not progress.get(ex_key):
                progress[ex_key] = True
                save_progress(username, progress)
                st.rerun()
        else:
            if progress.get(ex_key):
                progress[ex_key] = False
                save_progress(username, progress)
                st.rerun()
        st.divider()

    if not is_day_done:
        all_c = all(progress.get(k, False) for k in day_keys)
        if st.button("COMPLETE WORKOUT", type="primary" if all_c else "secondary"):
            if all_c: completion_dialog(day_label, username, day_key, week)
            else: st.warning("Finish all exercises.")

    /* 5. Add space between exercises so you don't mis-click */
    hr {
        margin-top: 2rem !important;
        margin-bottom: 2rem !important;
        border-top: 2px solid #444 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- THE REST OF YOUR WORKING CODE STARTING HERE ---
if 'page' not in st.session_state:
    st.session_state['page'] = 'login'

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

# PAGE 1: LOGIN
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

# PAGE 2: SELECTION
elif st.session_state['page'] == 'selection':
    username = st.session_state['username']
    schedule = load_user_schedule(username)
    st.title("Main Menu")
    sel_week = st.selectbox("Select Training Week", ["1", "2", "3", "4"])
    day_map = {}
    for d in ["1", "2", "3", "4"]:
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

# PAGE 3: WORKOUT
elif st.session_state['page'] == 'workout':
    username = st.session_state['username']
    week = st.session_state['sel_week']
    day_key = st.session_state['sel_day_key']
    day_label = st.session_state['sel_day_label']
    schedule = load_user_schedule(username)
    progress = load_progress(username)
    is_day_done = progress.get(f"day_done_w{week}_d{day_key}", False)

    header_col, menu_col = st.columns([3, 1])
    with header_col:
        st.caption(f"WEEK {week}")
        st.subheader(day_label)
    with menu_col:
        if st.button("Menu ☰"):
            st.session_state['page'] = 'selection'
            st.rerun()

    st.divider()
    exercises = schedule['weeks'][week].get(day_key, [])
    day_exercise_keys = []

    for ex_idx, ex in enumerate(exercises):
        ex_key = f"{username}_w{week}_d{day_key}_ex{ex_idx}"
        day_exercise_keys.append(ex_key)
        st.markdown(f"**:blue[{ex['exercise'].upper()}]**")
        sets_text = " • ".join([f"{s['reps']}x{s['weight']}" for s in ex['sets']])
        st.markdown(f'<div style="font-size: 1.6rem; margin-bottom: 10px;">{sets_text}</div>', unsafe_allow_html=True)
        
        # BACK TO ORIGINAL CHECKBOX LOGIC
        checked = st.checkbox("DONE", value=progress.get(ex_key, False), key=ex_key, disabled=is_day_done)
        if checked != progress.get(ex_key, False):
            progress[ex_key] = checked
            save_progress(username, progress)
            st.rerun()
        st.divider()

    all_checked = all(progress.get(k, False) for k in day_exercise_keys)
    if not is_day_done:
        btn_style = "primary" if all_checked else "secondary"
        if st.button("COMPLETE WORKOUT", type=btn_style):
            if all_checked:
                completion_dialog(day_label, username, day_key, week)
            else:
                st.warning("Finish all exercises.")

