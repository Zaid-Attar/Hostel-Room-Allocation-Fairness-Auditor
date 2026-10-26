"""
Pure Mathematical Audit Engine for Hostel Room Allocation Fairness Auditor (HRAFA).
Implements the 12 algorithmic steps defined in Section 6 of the Work Plan.
This module contains pure functions and has NO direct database access so that it can be
tested and executed independently.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats

# Section 5.2 / Section 6: Category bonus constants
CATEGORY_BONUS: Dict[str, float] = {
    "General": 0.0,
    "OBC": 0.5,
    "EWS": 0.5,
    "SC": 1.0,
    "ST": 1.0,
}

DEFAULT_POLICY_WEIGHTS: Dict[str, float] = {
    "w_cgpa": 0.35,
    "w_distance": 0.20,
    "w_year": 0.20,
    "w_category": 0.10,
    "w_special_needs": 0.15,
    "w_room_mess": 0.60,
    "w_room_floor": 0.40,
    "tolerance_pct": 10.0,
}


def compute_priority_score(
    row: pd.Series,
    max_distance: float,
    weights: Dict[str, float]
) -> float:
    """
    Step 1: Priority score.
    Normalize each factor to 0..1:
      cgpa / 10, distance_km / max distance, year / 4, category bonus, special_needs (0 or 1).
    Score = 100 * (weighted sum) / (sum of weights).
    """
    w_sum = (
        weights["w_cgpa"]
        + weights["w_distance"]
        + weights["w_year"]
        + weights["w_category"]
        + weights["w_special_needs"]
    )
    if w_sum <= 0:
        return 0.0

    norm_cgpa = float(row.get("cgpa", 0.0)) / 10.0
    safe_max_dist = max_distance if max_distance > 0 else 1.0
    norm_dist = min(float(row.get("distance_km", 0.0)) / safe_max_dist, 1.0)
    norm_year = float(row.get("year", 1)) / 4.0
    cat_bonus = CATEGORY_BONUS.get(str(row.get("category", "General")), 0.0)
    special = 1.0 if int(row.get("special_needs", 0)) == 1 else 0.0

    weighted = (
        weights["w_cgpa"] * norm_cgpa
        + weights["w_distance"] * norm_dist
        + weights["w_year"] * norm_year
        + weights["w_category"] * cat_bonus
        + weights["w_special_needs"] * special
    )
    return round((weighted / w_sum) * 100.0, 2)


def compute_room_quality(
    row: pd.Series,
    max_mess: float,
    max_floor: float,
    weights: Dict[str, float]
) -> float:
    """
    Step 2: Room quality.
    Quality = (w_room_mess * (1 - mess_dist/max_mess) + w_room_floor * (1 - floor/max_floor))
              / (sum of the two weights) * 100.
    """
    w_sum = weights["w_room_mess"] + weights["w_room_floor"]
    if w_sum <= 0:
        return 0.0

    safe_max_mess = max_mess if max_mess > 0 else 1.0
    safe_max_floor = max_floor if max_floor > 0 else 1.0

    mess_val = float(row.get("mess_distance_m", 0))
    floor_val = float(row.get("floor", 0))

    norm_mess = 1.0 - (min(mess_val, safe_max_mess) / safe_max_mess)
    norm_floor = 1.0 - (min(floor_val, safe_max_floor) / safe_max_floor)

    weighted = weights["w_room_mess"] * norm_mess + weights["w_room_floor"] * norm_floor
    return round((weighted / w_sum) * 100.0, 2)


def get_distance_band(distance_km: float) -> str:
    """Assigns distance to standard demographic bands."""
    if distance_km <= 100:
        return "0 to 100 km"
    elif distance_km <= 300:
        return "101 to 300 km"
    elif distance_km <= 600:
        return "301 to 600 km"
    else:
        return "Over 600 km"


def run_audit(
    students_df: pd.DataFrame,
    rooms_df: pd.DataFrame,
    allocations_df: pd.DataFrame,
    policy_overrides: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Executes the complete audit pipeline across all students and rooms.
    Returns:
      - summary: KPIs (fairness_score, violations_count, total_students, compliance_rate, etc.)
      - students: Audited records for each student with expected vs actual, deviation, status, percentiles
      - displacement_pairs: "Who got it vs who should have" pairs
      - group_stats: Breakdown by category, year, distance_band, and gender
      - corrected_allocations: Expected allocation DataFrame
    """
    weights = dict(DEFAULT_POLICY_WEIGHTS)
    if policy_overrides:
        weights.update(policy_overrides)

    tolerance_pct = float(weights.get("tolerance_pct", 10.0))

    students = students_df.copy()
    rooms = rooms_df.copy()
    alloc = allocations_df.copy()

    # Create quick lookups
    alloc_map = dict(zip(alloc["student_id"], alloc["room_id"])) if not alloc.empty else {}
    room_dict = rooms.set_index("room_id").to_dict(orient="index") if not rooms.empty else {}

    max_dist = float(students["distance_km"].max()) if not students.empty else 1.0

    audited_students: List[Dict[str, Any]] = []
    corrected_allocations: List[Dict[str, Any]] = []

    # Step 3: Run separately for M and F pools
    genders = ["M", "F"] if "gender" in students.columns else ["ALL"]

    for gender in genders:
        std_pool = students[students["gender"] == gender].copy() if gender in ["M", "F"] else students.copy()
        rm_pool = rooms[rooms["gender"] == gender].copy() if gender in ["M", "F"] else rooms.copy()

        if std_pool.empty:
            continue

        # Compute priority scores for students in pool
        std_pool["priority_score"] = std_pool.apply(
            lambda r: compute_priority_score(r, max_dist, weights), axis=1
        )

        # Compute room quality for rooms in pool
        max_mess = float(rm_pool["mess_distance_m"].max()) if not rm_pool.empty else 1.0
        max_flr = float(rm_pool["floor"].max()) if not rm_pool.empty else 1.0
        if not rm_pool.empty:
            rm_pool["quality_score"] = rm_pool.apply(
                lambda r: compute_room_quality(r, max_mess, max_flr, weights), axis=1
            )
            # Rank rooms by quality descending, tie-break by room_id ascending
            rm_pool = rm_pool.sort_values(by=["quality_score", "room_id"], ascending=[False, True]).reset_index(drop=True)
            rm_pool["room_rank"] = range(1, len(rm_pool) + 1)
        else:
            rm_pool["quality_score"] = []
            rm_pool["room_rank"] = []

        pool_room_rank_map = dict(zip(rm_pool["room_id"], rm_pool["room_rank"])) if not rm_pool.empty else {}
        pool_room_qual_map = dict(zip(rm_pool["room_id"], rm_pool["quality_score"])) if not rm_pool.empty else {}

        # Rank students by priority descending, tie-break by higher cgpa, then student_id ascending
        std_pool = std_pool.sort_values(
            by=["priority_score", "cgpa", "student_id"],
            ascending=[False, False, True]
        ).reset_index(drop=True)
        std_pool["priority_rank"] = range(1, len(std_pool) + 1)

        # Step 4: Expected allocation
        # Special-needs students take best accessible room; remaining take best remaining in order
        assigned_room_ids = set()
        expected_matches: Dict[str, str] = {}

        pwd_students = std_pool[std_pool["special_needs"] == 1]
        for _, s in pwd_students.iterrows():
            avail_acc = rm_pool[
                (rm_pool["accessible"] == 1) & (~rm_pool["room_id"].isin(assigned_room_ids))
            ]
            if not avail_acc.empty:
                chosen_rid = avail_acc.iloc[0]["room_id"]
                assigned_room_ids.add(chosen_rid)
                expected_matches[s["student_id"]] = chosen_rid

        rem_students = std_pool[~std_pool["student_id"].isin(expected_matches)]
        for _, s in rem_students.iterrows():
            avail_rem = rm_pool[~rm_pool["room_id"].isin(assigned_room_ids)]
            if not avail_rem.empty:
                chosen_rid = avail_rem.iloc[0]["room_id"]
                assigned_room_ids.add(chosen_rid)
                expected_matches[s["student_id"]] = chosen_rid

        # Step 6: Tolerance = tolerance_pct percent of pool room count, at least 1
        pool_room_count = len(rm_pool)
        tolerance = max(1, int(round((tolerance_pct * pool_room_count) / 100.0)))

        # Evaluate each student in this pool
        n_students = len(std_pool)
        for _, s in std_pool.iterrows():
            sid = s["student_id"]
            p_score = s["priority_score"]
            p_rank = s["priority_rank"]
            exp_rid = expected_matches.get(sid, None)
            act_rid = alloc_map.get(sid, None)

            # Record corrected allocation
            if exp_rid:
                corrected_allocations.append({
                    "student_id": sid,
                    "expected_room_id": exp_rid,
                    "gender": gender,
                    "priority_score": p_score,
                    "priority_rank": p_rank
                })

            exp_rank = pool_room_rank_map.get(exp_rid) if exp_rid else None
            act_rank = pool_room_rank_map.get(act_rid) if act_rid else None

            # Step 5: Deviation
            # Deviation = actual_room_rank - expected_room_rank.
            # Negative means better room than deserved. Positive means worse room.
            if act_rank is not None and exp_rank is not None:
                deviation = int(act_rank - exp_rank)
            else:
                deviation = None

            # Step 7: Hard Rule Check
            # Special needs student in non-accessible actual room
            is_pwd = int(s.get("special_needs", 0)) == 1
            act_room_meta = room_dict.get(act_rid, {}) if act_rid else {}
            act_is_accessible = int(act_room_meta.get("accessible", 0)) == 1 if act_rid else False

            hard_rule_violation = False
            violation_type = None
            if is_pwd and act_rid and not act_is_accessible:
                hard_rule_violation = True
                violation_type = "SPECIAL_NEEDS_NOT_ACCESSIBLE"

            # Step 6: Status determination
            if act_rid is None:
                status = "UNALLOCATED"
            elif deviation is None:
                status = "FAIR"
            elif deviation < -tolerance:
                status = "OVER_FAVORED"
            elif deviation > tolerance:
                status = "UNDER_SERVED"
            else:
                status = "FAIR"

            # A student is flagged if status != FAIR or hard rule violated
            is_flagged = (status != "FAIR") or hard_rule_violation

            # Step 8: Plot Percentiles (0 to 100 with 100 as best)
            priority_pct = round(100.0 - ((p_rank - 1) / max(1, n_students - 1)) * 100.0, 1) if n_students > 1 else 100.0
            if act_rank and pool_room_count > 1:
                room_qual_pct = round(100.0 - ((act_rank - 1) / max(1, pool_room_count - 1)) * 100.0, 1)
            elif act_rank:
                room_qual_pct = 100.0
            else:
                room_qual_pct = 0.0

            act_quality = pool_room_qual_map.get(act_rid, 0.0) if act_rid else None

            # Step 12: Plain English reason
            reason_parts = []
            if hard_rule_violation:
                reason_parts.append(
                    f"PwD student assigned to non-accessible upper room ({act_rid}, Floor {act_room_meta.get('floor')})."
                )
            if status == "OVER_FAVORED":
                reason_parts.append(
                    f"Over-favored: Received Rank {act_rank} room ({act_rid}), but priority entitled Rank {exp_rank} (gap: {deviation})."
                )
            elif status == "UNDER_SERVED":
                reason_parts.append(
                    f"Under-served: Demoted to Rank {act_rank} room ({act_rid}), though entitled to Rank {exp_rank} (gap: +{deviation})."
                )
            elif status == "UNALLOCATED":
                reason_parts.append(
                    f"Unallocated: No room assigned, but entitled to room {exp_rid} (Rank {exp_rank})."
                )
            else:
                reason_parts.append("Allocation is fair within policy tolerance.")

            audited_students.append({
                "student_id": sid,
                "name": s["name"],
                "gender": gender,
                "year": int(s["year"]),
                "cgpa": float(s["cgpa"]),
                "category": str(s["category"]),
                "distance_km": float(s["distance_km"]),
                "distance_band": get_distance_band(float(s["distance_km"])),
                "special_needs": int(s["special_needs"]),
                "priority_score": p_score,
                "priority_rank": p_rank,
                "priority_percentile": priority_pct,
                "expected_room_id": exp_rid,
                "expected_room_rank": exp_rank,
                "actual_room_id": act_rid,
                "actual_room_rank": act_rank,
                "actual_room_quality": act_quality,
                "room_quality_percentile": room_qual_pct,
                "deviation": deviation,
                "status": status,
                "hard_rule_violation": 1 if hard_rule_violation else 0,
                "violation_type": violation_type,
                "is_flagged": is_flagged,
                "reason": " ".join(reason_parts),
            })

    df_audited = pd.DataFrame(audited_students)

    # Step 9: Fairness score via Spearman correlation
    # Compute Spearman correlation between priority score and actual room quality across allocated students
    allocated_df = df_audited[df_audited["actual_room_id"].notna()].copy()
    if len(allocated_df) >= 2 and allocated_df["priority_score"].nunique() > 1 and allocated_df["actual_room_quality"].nunique() > 1:
        rho, _ = stats.spearmanr(allocated_df["priority_score"], allocated_df["actual_room_quality"])
        if np.isnan(rho):
            rho = 0.0
    else:
        rho = 1.0

    fairness_score = int(round(max(0.0, float(rho)) * 100.0))
    total_students = len(df_audited)
    fair_count = int((df_audited["status"] == "FAIR").sum())
    flagged_count = int(df_audited["is_flagged"].sum())
    hard_violations = int((df_audited["hard_rule_violation"] == 1).sum())
    compliance_rate = round((fair_count / total_students) * 100.0, 1) if total_students > 0 else 100.0

    # Step 10: Displacement pairs ("Who got it vs who should have")
    # For each flagged student, find the student who was expected to hold their actual room
    displacement_pairs = []
    audited_records = df_audited.to_dict(orient="records")
    exp_room_to_student = {
        row["expected_room_id"]: row
        for row in audited_records
        if row["expected_room_id"] is not None
    }

    seen_pairs = set()
    for victim in [r for r in audited_records if r["is_flagged"]]:
        act_room = victim["actual_room_id"]
        if not act_room:
            continue
        expected_holder = exp_room_to_student.get(act_room)
        if expected_holder is not None and expected_holder["student_id"] != victim["student_id"]:
            pair_key = (act_room, expected_holder["student_id"], victim["student_id"])
            if pair_key not in seen_pairs:
                seen_pairs.add(pair_key)
                gap = round(float(expected_holder["priority_score"]) - float(victim["priority_score"]), 2)
                displacement_pairs.append({
                    "room_id": act_room,
                    "should_have": expected_holder["student_id"],
                    "should_have_name": expected_holder["name"],
                    "should_have_priority": expected_holder["priority_score"],
                    "got_it": victim["student_id"],
                    "got_it_name": victim["name"],
                    "got_it_priority": victim["priority_score"],
                    "priority_gap": gap,
                })

    # Sort displacement pairs by priority gap descending
    displacement_pairs.sort(key=lambda x: x["priority_gap"], reverse=True)

    # Step 11: Demographic Group Statistics
    group_stats: Dict[str, List[Dict[str, Any]]] = {}
    for group_col in ["category", "year", "distance_band", "gender"]:
        stats_list = []
        for g_val, sub in df_audited.groupby(group_col):
            cnt = len(sub)
            valid_devs = sub["deviation"].dropna()
            avg_dev = round(float(valid_devs.mean()), 2) if not valid_devs.empty else 0.0
            flg_cnt = int(sub["is_flagged"].sum())
            flg_pct = round((flg_cnt / cnt) * 100.0, 1) if cnt > 0 else 0.0

            stats_list.append({
                "group": str(g_val),
                "count": cnt,
                "average_deviation": avg_dev,
                "flagged_count": flg_cnt,
                "flagged_percent": flg_pct,
            })
        group_stats[group_col] = stats_list

    return {
        "summary": {
            "fairness_score": fairness_score,
            "spearman_rho": round(float(rho), 4),
            "total_students": total_students,
            "total_allocated": len(allocated_df),
            "flagged_count": flagged_count,
            "flagged_rate": round((flagged_count / total_students) * 100.0, 1) if total_students > 0 else 0.0,
            "fair_count": fair_count,
            "compliance_rate": compliance_rate,
            "hard_rule_violations": hard_violations,
            "tolerance_used": tolerance,
        },
        "students": audited_students,
        "displacement_pairs": displacement_pairs,
        "group_stats": group_stats,
        "corrected_allocations": corrected_allocations,
    }


def explain_student(
    student_record: Dict[str, Any],
    max_distance: float,
    weights: Dict[str, float]
) -> Dict[str, Any]:
    """
    Step 12: Explainability Breakdown for an individual student.
    Returns weighted contributions of each factor, room comparison, and plain English explanation.
    """
    w_sum = (
        weights["w_cgpa"]
        + weights["w_distance"]
        + weights["w_year"]
        + weights["w_category"]
        + weights["w_special_needs"]
    )
    safe_max_dist = max_distance if max_distance > 0 else 1.0

    norm_cgpa = float(student_record.get("cgpa", 0.0)) / 10.0
    norm_dist = min(float(student_record.get("distance_km", 0.0)) / safe_max_dist, 1.0)
    norm_year = float(student_record.get("year", 1)) / 4.0
    cat_bonus = CATEGORY_BONUS.get(str(student_record.get("category", "General")), 0.0)
    special = 1.0 if int(student_record.get("special_needs", 0)) == 1 else 0.0

    factors = {
        "cgpa": {
            "raw_value": student_record.get("cgpa"),
            "weight": weights["w_cgpa"],
            "normalized": round(norm_cgpa, 3),
            "contribution": round((weights["w_cgpa"] * norm_cgpa / w_sum) * 100.0, 2),
        },
        "distance": {
            "raw_value": f"{student_record.get('distance_km')} km",
            "weight": weights["w_distance"],
            "normalized": round(norm_dist, 3),
            "contribution": round((weights["w_distance"] * norm_dist / w_sum) * 100.0, 2),
        },
        "year": {
            "raw_value": f"Year {student_record.get('year')}",
            "weight": weights["w_year"],
            "normalized": round(norm_year, 3),
            "contribution": round((weights["w_year"] * norm_year / w_sum) * 100.0, 2),
        },
        "category": {
            "raw_value": student_record.get("category"),
            "weight": weights["w_category"],
            "bonus_value": cat_bonus,
            "contribution": round((weights["w_category"] * cat_bonus / w_sum) * 100.0, 2),
        },
        "special_needs": {
            "raw_value": bool(student_record.get("special_needs")),
            "weight": weights["w_special_needs"],
            "value": special,
            "contribution": round((weights["w_special_needs"] * special / w_sum) * 100.0, 2),
        },
    }

    return {
        "student_id": student_record.get("student_id"),
        "name": student_record.get("name"),
        "priority_score": student_record.get("priority_score"),
        "expected_room_id": student_record.get("expected_room_id"),
        "expected_room_rank": student_record.get("expected_room_rank"),
        "actual_room_id": student_record.get("actual_room_id"),
        "actual_room_rank": student_record.get("actual_room_rank"),
        "deviation": student_record.get("deviation"),
        "status": student_record.get("status"),
        "hard_rule_violation": bool(student_record.get("hard_rule_violation")),
        "reason": student_record.get("reason"),
        "factors": factors,
    }
