"""
Reproducible Synthetic Data Generator for Hostel Room Allocation Fairness Auditor.
Generates:
  1. 300 students (150 M, 150 F) with realistic CGPA, category, year, distance, and special needs.
  2. 300 rooms (150 M, 150 F) with floor, mess distance, and accessibility flag.
  3. Official allocation with planted violations:
     - 8% large rank gap swaps (with mild systematic bias against OBC)
     - 3 special needs students placed in upper-floor (non-accessible) rooms
     - 2 unallocated students (excluded from allocation.csv)
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR / "data"

RANDOM_SEED = 42
BIASED_CATEGORY = "OBC"

CATEGORY_MAP = {
    "General": 0.0,
    "OBC": 0.5,
    "EWS": 0.5,
    "SC": 1.0,
    "ST": 1.0
}

DEFAULT_POLICY = {
    "w_cgpa": 0.35,
    "w_distance": 0.20,
    "w_year": 0.20,
    "w_category": 0.10,
    "w_special_needs": 0.15,
    "w_room_mess": 0.60,
    "w_room_floor": 0.40,
    "tolerance_pct": 10.0
}

FIRST_NAMES_M = [
    "Aarav", "Rohan", "Aditya", "Tanmay", "Kunal", "Vikram", "Rahul", "Arjun",
    "Siddharth", "Gaurav", "Nikhil", "Omkar", "Varun", "Manish", "Pranav", "Akshay",
    "Harsh", "Sameer", "Yash", "Ayush", "Atharva", "Chinmay", "Digvijay", "Hrishikesh"
]

FIRST_NAMES_F = [
    "Ananya", "Priya", "Sneha", "Ishita", "Meera", "Neha", "Pooja", "Kavya",
    "Riya", "Shreya", "Divya", "Sakshi", "Isha", "Ankita", "Radhika", "Sayali",
    "Tanvi", "Srushti", "Aditi", "Mrunal", "Krutika", "Bhakti", "Sanika", "Vaishnavi"
]

LAST_NAMES = [
    "Sharma", "Patil", "Kulkarni", "Deshmukh", "Joshi", "Verma", "Tiwari", "Attar",
    "Chilvery", "Bhure", "Shinde", "Pawar", "Gupta", "Mehta", "Bane", "More",
    "Jadhav", "Bhosale", "Chavan", "Kadam", "Rao", "Nair", "Iyer", "Reddy"
]

def generate_students(seed: int = RANDOM_SEED) -> pd.DataFrame:
    np.random.seed(seed)
    categories = ["General", "OBC", "SC", "ST", "EWS"]
    cat_weights = [0.45, 0.27, 0.12, 0.06, 0.10]

    records = []
    # 150 Males
    for i in range(150):
        sid = f"S_M_{i+1:03d}"
        fname = np.random.choice(FIRST_NAMES_M)
        lname = np.random.choice(LAST_NAMES)
        name = f"{fname} {lname}"
        cgpa = round(float(np.clip(np.random.normal(7.5, 1.0), 5.0, 10.0)), 2)
        year = int(np.random.choice([1, 2, 3, 4], p=[0.28, 0.26, 0.24, 0.22]))
        category = np.random.choice(categories, p=cat_weights)
        dist = int(np.clip(np.random.exponential(scale=350) + 15, 5, 1500))
        # ~4% special needs
        special = 1 if i < 6 else 0
        records.append({
            "student_id": sid,
            "name": name,
            "gender": "M",
            "year": year,
            "cgpa": cgpa,
            "category": category,
            "distance_km": dist,
            "special_needs": special
        })

    # 150 Females
    for i in range(150):
        sid = f"S_F_{i+1:03d}"
        fname = np.random.choice(FIRST_NAMES_F)
        lname = np.random.choice(LAST_NAMES)
        name = f"{fname} {lname}"
        cgpa = round(float(np.clip(np.random.normal(7.5, 1.0), 5.0, 10.0)), 2)
        year = int(np.random.choice([1, 2, 3, 4], p=[0.28, 0.26, 0.24, 0.22]))
        category = np.random.choice(categories, p=cat_weights)
        dist = int(np.clip(np.random.exponential(scale=350) + 15, 5, 1500))
        special = 1 if i < 6 else 0
        records.append({
            "student_id": sid,
            "name": name,
            "gender": "F",
            "year": year,
            "cgpa": cgpa,
            "category": category,
            "distance_km": dist,
            "special_needs": special
        })

    df = pd.DataFrame(records)
    # Shuffle slightly so special needs aren't purely at the very beginning
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df

def generate_rooms(seed: int = RANDOM_SEED) -> pd.DataFrame:
    np.random.seed(seed)
    records = []

    # 150 Boys Rooms
    for i in range(150):
        rid = f"R_B_{i+1:03d}"
        floor = (i // 30) % 5  # Floors 0, 1, 2, 3, 4 (30 rooms each)
        mess_dist = int(np.clip(30 + floor * 40 + np.random.randint(-15, 25), 20, 400))
        accessible = 1 if floor == 0 else 0
        records.append({
            "room_id": rid,
            "hostel": "Boys Block Alpha",
            "gender": "M",
            "floor": floor,
            "mess_distance_m": mess_dist,
            "accessible": accessible
        })

    # 150 Girls Rooms
    for i in range(150):
        rid = f"R_G_{i+1:03d}"
        floor = (i // 30) % 5  # Floors 0, 1, 2, 3, 4 (30 rooms each)
        mess_dist = int(np.clip(30 + floor * 40 + np.random.randint(-15, 25), 20, 400))
        accessible = 1 if floor == 0 else 0
        records.append({
            "room_id": rid,
            "hostel": "Girls Block Beta",
            "gender": "F",
            "floor": floor,
            "mess_distance_m": mess_dist,
            "accessible": accessible
        })

    return pd.DataFrame(records)

def compute_priority(df: pd.DataFrame, max_dist: float) -> pd.Series:
    p = DEFAULT_POLICY
    norm_cgpa = df["cgpa"] / 10.0
    norm_dist = df["distance_km"] / (max_dist if max_dist > 0 else 1.0)
    norm_year = df["year"] / 4.0
    cat_bonus = df["category"].map(CATEGORY_MAP).fillna(0.0)
    special = df["special_needs"].astype(float)

    sum_w = p["w_cgpa"] + p["w_distance"] + p["w_year"] + p["w_category"] + p["w_special_needs"]
    w_sum = (
        p["w_cgpa"] * norm_cgpa +
        p["w_distance"] * norm_dist +
        p["w_year"] * norm_year +
        p["w_category"] * cat_bonus +
        p["w_special_needs"] * special
    )
    score = (w_sum / sum_w) * 100.0
    return np.round(score, 2)

def compute_room_quality(df: pd.DataFrame, max_mess: float, max_floor: float) -> pd.Series:
    p = DEFAULT_POLICY
    norm_mess = 1.0 - (df["mess_distance_m"] / (max_mess if max_mess > 0 else 1.0))
    norm_floor = 1.0 - (df["floor"] / (max_floor if max_floor > 0 else 1.0))

    sum_w = p["w_room_mess"] + p["w_room_floor"]
    w_sum = p["w_room_mess"] * norm_mess + p["w_room_floor"] * norm_floor
    quality = (w_sum / sum_w) * 100.0
    return np.round(quality, 2)

def compute_ideal_allocation(students_df: pd.DataFrame, rooms_df: pd.DataFrame) -> pd.DataFrame:
    allocations = []
    max_dist = float(students_df["distance_km"].max())

    for gender in ["M", "F"]:
        std_pool = students_df[students_df["gender"] == gender].copy()
        rm_pool = rooms_df[rooms_df["gender"] == gender].copy()

        std_pool["priority"] = compute_priority(std_pool, max_dist)
        rm_pool["quality"] = compute_room_quality(
            rm_pool,
            float(rm_pool["mess_distance_m"].max()),
            float(rm_pool["floor"].max())
        )

        # Sort rooms by quality descending, room_id ascending
        rm_pool = rm_pool.sort_values(by=["quality", "room_id"], ascending=[False, True]).reset_index(drop=True)
        # Sort students by priority descending, cgpa descending, student_id ascending
        std_pool = std_pool.sort_values(by=["priority", "cgpa", "student_id"], ascending=[False, False, True]).reset_index(drop=True)

        assigned_rooms = set()
        std_assigned = {}

        # 1. Special needs take best accessible rooms
        pwd_students = std_pool[std_pool["special_needs"] == 1]
        for _, s in pwd_students.iterrows():
            avail = rm_pool[(rm_pool["accessible"] == 1) & (~rm_pool["room_id"].isin(assigned_rooms))]
            if not avail.empty:
                chosen_room = avail.iloc[0]["room_id"]
                assigned_rooms.add(chosen_room)
                std_assigned[s["student_id"]] = chosen_room

        # 2. Remaining students take best remaining rooms
        rem_students = std_pool[~std_pool["student_id"].isin(std_assigned)]
        for _, s in rem_students.iterrows():
            avail = rm_pool[~rm_pool["room_id"].isin(assigned_rooms)]
            if not avail.empty:
                chosen_room = avail.iloc[0]["room_id"]
                assigned_rooms.add(chosen_room)
                std_assigned[s["student_id"]] = chosen_room

        for sid, rid in std_assigned.items():
            allocations.append({"student_id": sid, "room_id": rid})

    return pd.DataFrame(allocations)

def plant_violations(alloc_df: pd.DataFrame, students_df: pd.DataFrame, rooms_df: pd.DataFrame) -> pd.DataFrame:
    """
    Plants realistic violations per Phase 1 instructions:
    - Small neighbor swaps within tolerance
    - ~8% large rank gap swaps (favouring OBC as under-served victims)
    - 3 special needs moved to upper floors
    - 2 students left unallocated
    """
    np.random.seed(RANDOM_SEED)
    alloc = alloc_df.copy()

    # Map lookups
    std_meta = students_df.set_index("student_id").to_dict(orient="index")
    rm_meta = rooms_df.set_index("room_id").to_dict(orient="index")

    # Add helper columns for sorting within gender
    alloc["gender"] = alloc["student_id"].apply(lambda s: std_meta[s]["gender"])
    alloc["cgpa"] = alloc["student_id"].apply(lambda s: std_meta[s]["cgpa"])

    new_alloc_rows = []

    for gender in ["M", "F"]:
        pool = alloc[alloc["gender"] == gender].copy().reset_index(drop=True)
        n = len(pool)

        # 1. Add small neighbor swaps (1-2 positions) that stay within tolerance
        for i in range(15, n - 20, 10):
            if np.random.rand() < 0.4:
                r1, r2 = pool.loc[i, "room_id"], pool.loc[i+1, "room_id"]
                pool.loc[i, "room_id"] = r2
                pool.loc[i+1, "room_id"] = r1

        # 2. Plant large rank gap swaps (~8% = 12 students per gender = 6 pairs)
        # Prioritize picking under-served victim from BIASED_CATEGORY (OBC)
        high_candidates = [
            idx for idx in range(3, 40)
            if std_meta[pool.loc[idx, "student_id"]]["special_needs"] == 0
        ]
        # Prefer OBC victims
        obc_high = [idx for idx in high_candidates if std_meta[pool.loc[idx, "student_id"]]["category"] == BIASED_CATEGORY]
        other_high = [idx for idx in high_candidates if idx not in obc_high]
        chosen_high = (obc_high + other_high)[:6]

        low_candidates = list(range(n - 45, n - 5))[:6]

        for h, l in zip(chosen_high, low_candidates):
            room_h = pool.loc[h, "room_id"]
            room_l = pool.loc[l, "room_id"]
            pool.loc[h, "room_id"] = room_l
            pool.loc[l, "room_id"] = room_h

        # 3. Move special-needs students into upper non-accessible rooms
        # 3 special-needs overall (e.g. 2 in M, 1 in F)
        num_pwd_violations = 2 if gender == "M" else 1
        pwd_indices = [
            idx for idx in range(n)
            if std_meta[pool.loc[idx, "student_id"]]["special_needs"] == 1
        ]
        upper_rooms = [
            rid for rid, r in rm_meta.items()
            if r["gender"] == gender and r["floor"] >= 2
        ]

        for k in range(min(num_pwd_violations, len(pwd_indices))):
            p_idx = pwd_indices[k]
            target_upper = upper_rooms[k * 5]
            # Find who has target_upper
            holder_idx = pool[pool["room_id"] == target_upper].index[0]
            curr_room = pool.loc[p_idx, "room_id"]

            pool.loc[p_idx, "room_id"] = target_upper
            pool.loc[holder_idx, "room_id"] = curr_room

        new_alloc_rows.append(pool)

    final_alloc = pd.concat(new_alloc_rows, ignore_index=True)[["student_id", "room_id"]]

    # 4. Leave 2 students unallocated (e.g., 1 M and 1 F)
    # Remove one male and one female student row from allocation
    unalloc_ids = ["S_M_149", "S_F_149"]
    final_alloc = final_alloc[~final_alloc["student_id"].isin(unalloc_ids)].reset_index(drop=True)

    return final_alloc

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating students dataset...")
    students_df = generate_students(RANDOM_SEED)
    students_csv_path = DATA_DIR / "students.csv"
    students_df.to_csv(students_csv_path, index=False)
    print(f"Saved {len(students_df)} students to {students_csv_path}")

    print("Generating rooms dataset...")
    rooms_df = generate_rooms(RANDOM_SEED)
    rooms_csv_path = DATA_DIR / "rooms.csv"
    rooms_df.to_csv(rooms_csv_path, index=False)
    print(f"Saved {len(rooms_df)} rooms to {rooms_csv_path}")

    print("Generating ideal allocations & planting violations...")
    ideal_alloc = compute_ideal_allocation(students_df, rooms_df)
    alloc_with_violations = plant_violations(ideal_alloc, students_df, rooms_df)
    alloc_csv_path = DATA_DIR / "allocation.csv"
    alloc_with_violations.to_csv(alloc_csv_path, index=False)
    print(f"Saved {len(alloc_with_violations)} allocations to {alloc_csv_path}")

    print("\n[OK] Data generation complete successfully.")

if __name__ == "__main__":
    main()
