import json
import os

# =================================================================
# DATABASE & FILE I/O LAYER
# This file handles reading and writing all user-specific data.
# Each user now gets their own unique .json files.
# =================================================================

def load_user_schedule(username):
    """
    Tries to load a schedule file specific to the logged-in user.
    Example: if username is 'fsalinas', it looks for 'schedule_fsalinas.json'.
    """
    filename = f"schedule_{username.lower()}.json"
    if not os.path.exists(filename):
        return None
    with open(filename, 'r') as f:
        return json.load(f)

def load_progress(username):
    """
    Loads the progress checkmarks for a specific user.
    Returns an empty dictionary {} if the user has no progress yet.
    """
    filename = f"{username.lower()}_progress.json"
    if not os.path.exists(filename):
        return {}
    with open(filename, 'r') as f:
        return json.load(f)

def save_progress(username, progress_data):
    """
    Saves the checkmark state to the user's personal progress file.
    This ensures User A never overwrites User B's data.
    """
    filename = f"{username.lower()}_progress.json"
    with open(filename, 'w') as f:
        # indent=4 makes the JSON file readable if you open it in a text editor
        json.dump(progress_data, f, indent=4)

# =================================================================
# ID & LOGIC HELPERS
# =================================================================

def get_ex_id(week, category, exercise):
    """
    Generates a unique string ID for an exercise block.
    Format: w[week]_[category]_[exercise_name]
    Example: 'w1_push_benchpress'
    
    We strip spaces/special characters so the ID is 'clean' for Streamlit keys.
    """
    clean_ex = "".join(filter(str.isalnum, exercise)).lower()
    return f"w{week}_{category}_{clean_ex}"

def is_set_completed(progress, set_id):
    """
    Helper to check if a specific ID is marked as True in the progress dict.
    Default to False if the ID doesn't exist.
    """
    return progress.get(set_id, False)

def toggle_set_completion(username, progress, set_id):
    """
    The 'Main Event' function for the checkboxes:
    1. Look up the current status of the exercise.
    2. Flip it (True -> False or False -> True).
    3. Update the dictionary.
    4. IMMEDIATELY save it to the user's specific file.
    """
    # Get current status, default to False if never checked before
    current_status = progress.get(set_id, False)
    
    # Flip the status
    progress[set_id] = not current_status
    
    # Save to the specific file for this user
    save_progress(username, progress) 
    
    # Return the updated dictionary so app531.py can update the UI
    return progress