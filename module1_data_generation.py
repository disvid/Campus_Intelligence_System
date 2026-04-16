"""
MODULE 1: Synthetic Data Generation
Smart Campus Intelligence System
Generates realistic 30-day datasets with noise, peaks, and missing values.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import random

# ─── Configuration ────────────────────────────────────────────────────────────
random.seed(42)
np.random.seed(42)

START_DATE = datetime(2024, 3, 1)
END_DATE   = datetime(2024, 3, 31)
DATE_RANGE = pd.date_range(start=START_DATE, end=END_DATE, freq='D')

BUILDINGS  = ['Academic Block A', 'Academic Block B', 'Library',
              'Hostel Block 1', 'Hostel Block 2', 'Admin Block']
LOCATIONS  = ['Academic Zone', 'Library', 'Cafeteria',
              'Sports Complex', 'Hostel Area', 'Admin Zone']
CLASSES    = [f'CS{i:03d}' for i in range(101, 116)] + \
             [f'ME{i:03d}' for i in range(201, 211)] + \
             [f'EE{i:03d}' for i in range(301, 311)]

NUM_STUDENTS = 1200

os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/cleaned', exist_ok=True)
os.makedirs('models', exist_ok=True)
os.makedirs('outputs', exist_ok=True)

# ─── Helper: is_weekend ────────────────────────────────────────────────────────
def is_weekend(dt):
    return dt.weekday() >= 5  # Saturday=5, Sunday=6

# ─── Helper: hour_weight ──────────────────────────────────────────────────────
def hour_weight(hour, weekend=False):
    """Return a multiplier reflecting realistic campus activity at a given hour."""
    if weekend:
        # Lower overall; small peak around lunch
        weights = {
            0: 0.02, 1: 0.01, 2: 0.01, 3: 0.01, 4: 0.01, 5: 0.02,
            6: 0.05, 7: 0.10, 8: 0.20, 9: 0.30, 10: 0.40, 11: 0.50,
            12: 0.60, 13: 0.55, 14: 0.45, 15: 0.35, 16: 0.30, 17: 0.40,
            18: 0.45, 19: 0.35, 20: 0.25, 21: 0.15, 22: 0.08, 23: 0.04
        }
    else:
        # Weekday: peaks at 9-11 AM, 1-3 PM, 7-9 PM
        weights = {
            0: 0.02, 1: 0.01, 2: 0.01, 3: 0.01, 4: 0.02, 5: 0.05,
            6: 0.15, 7: 0.35, 8: 0.65, 9: 0.90, 10: 0.95, 11: 0.85,
            12: 0.70, 13: 0.80, 14: 0.85, 15: 0.75, 16: 0.60, 17: 0.55,
            18: 0.65, 19: 0.80, 20: 0.75, 21: 0.50, 22: 0.25, 23: 0.08
        }
    return weights.get(hour, 0.1)


# ════════════════════════════════════════════════════════════════════════════════
# 1. ATTENDANCE LOGS
# ════════════════════════════════════════════════════════════════════════════════
def generate_attendance():
    print("Generating attendance data...")
    records = []
    student_ids = [f'STU{i:04d}' for i in range(1, NUM_STUDENTS + 1)]

    for date in DATE_RANGE:
        weekend = is_weekend(date)
        # Fewer classes on weekends
        daily_classes = random.sample(CLASSES, k=5 if weekend else 18)

        for class_id in daily_classes:
            # Each class has 25–55 students enrolled
            enrolled = random.sample(student_ids, k=random.randint(25, 55))
            for stu_id in enrolled:
                # Weekend attendance lower; some students always absent
                if weekend:
                    status = np.random.choice(['Present', 'Absent'],
                                              p=[0.55, 0.45])
                else:
                    status = np.random.choice(['Present', 'Absent'],
                                              p=[0.82, 0.18])
                records.append({
                    'student_id':        stu_id,
                    'date':              date.strftime('%Y-%m-%d'),
                    'class_id':          class_id,
                    'attendance_status': status
                })

    df = pd.DataFrame(records)

    # Inject ~3% missing values
    missing_idx = df.sample(frac=0.03).index
    df.loc[missing_idx, 'attendance_status'] = np.nan

    df.to_csv('data/raw/attendance.csv', index=False)
    print(f"  → {len(df):,} attendance records saved.")
    return df


# ════════════════════════════════════════════════════════════════════════════════
# 2. WIFI USAGE
# ════════════════════════════════════════════════════════════════════════════════
def generate_wifi():
    print("Generating WiFi usage data...")
    records = []

    for date in DATE_RANGE:
        weekend = is_weekend(date)
        for hour in range(24):
            w = hour_weight(hour, weekend)
            for loc in LOCATIONS:
                # Location multipliers
                loc_mult = {
                    'Academic Zone':  1.4,
                    'Library':        1.1,
                    'Cafeteria':      0.7,
                    'Sports Complex': 0.4,
                    'Hostel Area':    0.9,
                    'Admin Zone':     0.5
                }.get(loc, 1.0)

                base_users = int(300 * w * loc_mult)
                users      = max(0, int(np.random.normal(base_users,
                                                         base_users * 0.20)))

                # Bandwidth: ~1.5 Mbps per user + noise
                bandwidth  = round(max(0.0, np.random.normal(
                    users * 1.5, users * 0.3)), 2)

                ts = datetime(date.year, date.month, date.day, hour,
                              random.randint(0, 59))

                records.append({
                    'timestamp':       ts.strftime('%Y-%m-%d %H:%M:%S'),
                    'location':        loc,
                    'number_of_users': users,
                    'bandwidth_usage': bandwidth   # in Mbps
                })

    df = pd.DataFrame(records)

    # Inject ~2% missing values
    missing_idx = df.sample(frac=0.02).index
    df.loc[missing_idx, ['number_of_users', 'bandwidth_usage']] = np.nan

    # Inject a few realistic spikes (exam week, events)
    spike_rows = df.sample(frac=0.005).index
    df.loc[spike_rows, 'number_of_users'] *= np.random.uniform(2.5, 4.0,
                                                                len(spike_rows))

    df.to_csv('data/raw/wifi_usage.csv', index=False)
    print(f"  → {len(df):,} WiFi records saved.")
    return df


# ════════════════════════════════════════════════════════════════════════════════
# 3. ELECTRICITY CONSUMPTION
# ════════════════════════════════════════════════════════════════════════════════
def generate_electricity():
    print("Generating electricity data...")
    records = []

    # Base consumption (units/hour) per building
    base_consumption = {
        'Academic Block A': 45,
        'Academic Block B': 40,
        'Library':          30,
        'Hostel Block 1':   25,
        'Hostel Block 2':   22,
        'Admin Block':      18
    }

    for date in DATE_RANGE:
        weekend = is_weekend(date)
        for hour in range(24):
            w = hour_weight(hour, weekend)
            for building in BUILDINGS:
                base = base_consumption[building]
                # Academic buildings near-zero after midnight on weekends
                if weekend and building.startswith('Academic') and hour < 7:
                    w_adj = 0.05
                elif building.startswith('Hostel') and (hour >= 22 or hour < 6):
                    w_adj = 0.9   # Hostels always on
                else:
                    w_adj = w

                units = max(0.5, np.random.normal(base * w_adj,
                                                  base * w_adj * 0.12))
                ts = datetime(date.year, date.month, date.day, hour, 0)

                records.append({
                    'timestamp':      ts.strftime('%Y-%m-%d %H:%M:%S'),
                    'building':       building,
                    'units_consumed': round(units, 3)
                })

    df = pd.DataFrame(records)

    # Inject ~1.5% missing values
    missing_idx = df.sample(frac=0.015).index
    df.loc[missing_idx, 'units_consumed'] = np.nan

    # Inject anomalous spikes (equipment fault simulation)
    spike_rows = df.sample(n=40).index
    df.loc[spike_rows, 'units_consumed'] *= np.random.uniform(3.0, 6.0, 40)

    df.to_csv('data/raw/electricity.csv', index=False)
    print(f"  → {len(df):,} electricity records saved.")
    return df


# ════════════════════════════════════════════════════════════════════════════════
# 4. MESS ENTRY DATA
# ════════════════════════════════════════════════════════════════════════════════
def generate_mess():
    print("Generating mess entry data...")
    records = []

    # Mess is open only during meal windows
    meal_windows = {
        'Breakfast': (7,  9,  400),
        'Lunch':     (12, 14, 900),
        'Snacks':    (16, 17, 350),
        'Dinner':    (19, 21, 850)
    }

    for date in DATE_RANGE:
        weekend = is_weekend(date)
        multiplier = 0.65 if weekend else 1.0

        for meal, (start_h, end_h, peak) in meal_windows.items():
            # Spread entries across the window (every 10 min)
            slot_minutes = list(range(start_h * 60, end_h * 60, 10))
            for mins in slot_minutes:
                hour   = mins // 60
                minute = mins % 60
                # Bell-curve spread across the window
                window_mid  = (start_h + end_h) / 2 * 60
                dist_factor = np.exp(-((mins - window_mid) ** 2) /
                                     (2 * (30 ** 2)))
                students = max(0, int(np.random.normal(
                    peak * dist_factor * multiplier,
                    peak * dist_factor * multiplier * 0.15 + 5
                )))

                ts = datetime(date.year, date.month, date.day, hour, minute)
                records.append({
                    'timestamp':          ts.strftime('%Y-%m-%d %H:%M:%S'),
                    'meal_type':          meal,
                    'number_of_students': students
                })

    df = pd.DataFrame(records)

    # Inject ~2% missing values
    missing_idx = df.sample(frac=0.02).index
    df.loc[missing_idx, 'number_of_students'] = np.nan

    df.to_csv('data/raw/mess_entry.csv', index=False)
    print(f"  → {len(df):,} mess entry records saved.")
    return df


# ════════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 55)
    print("  Smart Campus — Module 1: Data Generation")
    print("=" * 55)
    att = generate_attendance()
    wifi = generate_wifi()
    elec = generate_electricity()
    mess = generate_mess()
    print("\nAll datasets generated in data/raw/")
    print(f"  Attendance :  {len(att):>8,} rows")
    print(f"  WiFi Usage :  {len(wifi):>8,} rows")
    print(f"  Electricity:  {len(elec):>8,} rows")
    print(f"  Mess Entry :  {len(mess):>8,} rows")