import pandas as pd
import os
import sys
import subprocess
import json

def create_new_user(username, password, template_choice):
    # Determine which template to use
    if template_choice.lower() == "standard":
        template_file = 'standard531_template.csv'
    elif template_choice.lower() == "modified":
        template_file = 'modified531_template.csv'
    else:
        print("❌ Error: Choose 'standard' or 'modified'.")
        return

    user_clean = username.lower().strip()
    progress_file = f"{user_clean}_progress.json"
    new_user_csv = f'input_{user_clean}.csv'

    # 1. CLEAR PROGRESS FIRST
    try:
        if os.path.exists(progress_file):
            os.remove(progress_file)
        with open(progress_file, 'w') as f:
            json.dump({}, f)
        print(f"🗑️  Cleared and initialized {progress_file}")
    except Exception as e:
        print(f"❌ Progress Error: {e}")
        return

    # 2. LOAD & NORMALIZE TEMPLATE
    if not os.path.exists(template_file):
        print(f"❌ Error: {template_file} not found!")
        return

    try:
        df = pd.read_csv(template_file)
        # Normalize headers (handles 'Day' vs 'day')
        df.columns = [str(c).strip().lower() for c in df.columns]

        # Inject Credentials
        user_row = {'exercise': user_clean, '5_rep_max': 0, 'day': 0, 'tags': 'username'}
        pass_row = {'exercise': password, '5_rep_max': 0, 'day': 0, 'tags': 'password'}

        df_new = pd.concat([pd.DataFrame([user_row, pass_row]), df], ignore_index=True)
        df_new.to_csv(new_user_csv, index=False)
        print(f"📝 Created {new_user_csv} using {template_choice} template.")

        # 3. RUN ENGINE
        subprocess.run([sys.executable, "engine531.py", user_clean])

    except Exception as e:
        print(f"❌ CSV Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 4:
        create_new_user(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("Usage: python newuser.py <username> <password> <standard/modified>")