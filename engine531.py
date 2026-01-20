import pandas as pd
import json
import sys
import os
import math

TRAINING_MAX_RATIO = 0.90

def round_to_nearest_5(number):
    if pd.isna(number):
        return 0
    return int(5 * round(number / 5))

def calculate_estimated_1rm(weight, reps):
    return weight * (1 + reps / 30)

def generate_schedule(user_arg):
    target_user = user_arg.lower().strip()
    input_csv = f"input_{target_user}.csv"
    output_json = f"schedule_{target_user}.json"

    try:
        df = pd.read_csv(input_csv)
        df.columns = [str(c).strip().lower() for c in df.columns]
    except Exception as e:
        print(f"❌ Engine Load Error: {e}")
        return

    # EXTRACT AUTH
    tags_col = df['tags'].fillna('').astype(str).str.lower().str.strip()
    u_mask, p_mask = (tags_col == 'username'), (tags_col == 'password')
    username_val = str(df.loc[u_mask, 'exercise'].values[0])
    password_val = str(df.loc[p_mask, 'exercise'].values[0])
    
    exercises_df = df[~(u_mask | p_mask)].copy()

    # Main Lift Waves
    waves = {
        1: {"pct": [0.65, 0.75, 0.85], "reps": [5, 5, 5]},
        2: {"pct": [0.70, 0.80, 0.90], "reps": [3, 3, 3]},
        3: {"pct": [0.75, 0.85, 0.95], "reps": [5, 3, 1]},
        4: {"pct": [0.40, 0.50, 0.60], "reps": [5, 5, 5]} 
    }

    # Accessory Waves: Adjusting Weight AND Reps
    # Week 1: High Volume/Mod Intensity
    # Week 2: Mod Volume/High Intensity
    # Week 3: Low Volume/Peak Intensity
    # Week 4: Low Volume/Low Intensity (Deload)
    acc_waves = {
        1: {"pct": 0.60, "sets": 3, "reps": 12},
        2: {"pct": 0.65, "sets": 3, "reps": 10},
        3: {"pct": 0.70, "sets": 4, "reps": 8},
        4: {"pct": 0.50, "sets": 2, "reps": 12} 
    }

    full_schedule = {"username": username_val, "password": password_val, "weeks": {}}

    for week_num in range(1, 5):
        wave = waves[week_num]
        acc_cfg = acc_waves[week_num]
        week_data = {"1": [], "2": [], "3": [], "4": []}
        
        for _, row in exercises_df.iterrows():
            if pd.isna(row['5_rep_max']): continue
            
            day_val = str(int(float(row['day']))) if pd.notnull(row['day']) else "1"
            tag = str(row['tags']).lower().strip()
            five_rm = float(row['5_rep_max'])
            
            entry = {"exercise": row['exercise'], "tags": tag, "sets": []}
            
            if tag == 'main':
                tm = calculate_estimated_1rm(five_rm, 5) * TRAINING_MAX_RATIO
                for i in range(3):
                    entry["sets"].append({
                        "reps": f"{wave['reps'][i]}{'+' if i==2 and week_num!=4 else ''}",
                        "weight": round_to_nearest_5(tm * wave["pct"][i]),
                        "type": "Main"
                    })
                if week_num != 4:
                    fsl_wt = round_to_nearest_5(tm * wave["pct"][0])
                    for _ in range(3): 
                        entry["sets"].append({"reps": 5, "weight": fsl_wt, "type": "FSL"})
            
            elif tag == 'core':
                plan = {1: [3, 12], 2: [3, 15], 3: [4, 12], 4: [2, 10]}
                s, r = plan[week_num]
                for _ in range(s): entry["sets"].append({"reps": r, "weight": "BW", "type": "Core"})
            
            else: # Accessory/Supplemental
                calc_weight = round_to_nearest_5(five_rm * acc_cfg["pct"])
                for _ in range(acc_cfg["sets"]): 
                    entry["sets"].append({
                        "reps": acc_cfg["reps"], 
                        "weight": calc_weight, 
                        "type": "Acc"
                    })

            if day_val in week_data:
                week_data[day_val].append(entry)

        full_schedule["weeks"][str(week_num)] = week_data

    with open(output_json, 'w') as f:
        json.dump(full_schedule, f, indent=4)
    print(f"🎉 Created schedule_{target_user}.json")

if __name__ == "__main__":
    if len(sys.argv) > 1: generate_schedule(sys.argv[1])