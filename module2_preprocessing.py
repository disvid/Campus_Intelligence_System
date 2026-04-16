"""
MODULE 2: Data Preprocessing
Smart Campus Intelligence System
Cleans raw datasets: handles missing values, removes outliers,
normalizes timestamps, and saves cleaned CSVs to data/cleaned/.
"""

import pandas as pd
import numpy as np
import os

os.makedirs('data/cleaned', exist_ok=True)


# ─── Generic helpers ──────────────────────────────────────────────────────────

def parse_timestamp(df, col='timestamp'):
    """Parse a timestamp column and extract time features."""
    df[col] = pd.to_datetime(df[col])
    df['date']       = df[col].dt.date
    df['hour']       = df[col].dt.hour
    df['day_of_week'] = df[col].dt.dayofweek   # 0=Monday
    df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
    df['week']       = df[col].dt.isocalendar().week.astype(int)
    return df


def remove_outliers_iqr(df, column, multiplier=3.0):
    """Remove rows where column value is outside IQR * multiplier."""
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - multiplier * IQR
    upper = Q3 + multiplier * IQR
    before = len(df)
    df = df[(df[column] >= lower) & (df[column] <= upper)]
    removed = before - len(df)
    if removed:
        print(f"    Removed {removed} outlier rows in '{column}'.")
    return df


def report_missing(df, name):
    missing = df.isnull().sum()
    total   = missing[missing > 0]
    if not total.empty:
        print(f"  Missing values in {name}:")
        for col, cnt in total.items():
            print(f"    {col}: {cnt} ({cnt/len(df)*100:.1f}%)")


# ════════════════════════════════════════════════════════════════════════════════
# 1. ATTENDANCE
# ════════════════════════════════════════════════════════════════════════════════
def preprocess_attendance():
    print("\n[1] Preprocessing attendance...")
    df = pd.read_csv('data/raw/attendance.csv')
    print(f"  Loaded {len(df):,} rows.")
    report_missing(df, 'attendance')

    # Fill missing attendance status as 'Absent' (conservative assumption)
    df['attendance_status'].fillna('Absent', inplace=True)

    # Convert date
    df['date'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date'].dt.dayofweek
    df['is_weekend']  = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
    df['month']       = df['date'].dt.month
    df['week']        = df['date'].dt.isocalendar().week.astype(int)

    # Binary encode attendance
    df['is_present'] = (df['attendance_status'] == 'Present').astype(int)

    # Deduplicate (same student, date, class)
    before = len(df)
    df.drop_duplicates(subset=['student_id', 'date', 'class_id'], inplace=True)
    print(f"  Removed {before - len(df)} duplicate rows.")

    df.to_csv('data/cleaned/attendance_clean.csv', index=False)
    print(f"  Saved {len(df):,} clean rows → data/cleaned/attendance_clean.csv")
    return df


# ════════════════════════════════════════════════════════════════════════════════
# 2. WIFI USAGE
# ════════════════════════════════════════════════════════════════════════════════
def preprocess_wifi():
    print("\n[2] Preprocessing WiFi usage...")
    df = pd.read_csv('data/raw/wifi_usage.csv')
    print(f"  Loaded {len(df):,} rows.")
    report_missing(df, 'wifi')

    # Fill missing numeric columns with median per location
    for col in ['number_of_users', 'bandwidth_usage']:
        df[col] = df.groupby('location')[col].transform(
            lambda x: x.fillna(x.median())
        )

    # Parse timestamp and extract features
    df = parse_timestamp(df)

    # Clip negatives
    df['number_of_users'] = df['number_of_users'].clip(lower=0)
    df['bandwidth_usage'] = df['bandwidth_usage'].clip(lower=0.0)

    # Remove outliers per location
    cleaned_parts = []
    for loc, group in df.groupby('location'):
        group = remove_outliers_iqr(group, 'number_of_users', multiplier=3.0)
        group = remove_outliers_iqr(group, 'bandwidth_usage',  multiplier=3.0)
        cleaned_parts.append(group)
    df = pd.concat(cleaned_parts).reset_index(drop=True)

    # Normalize bandwidth (users may be 0 → avoid div/0)
    df['bandwidth_per_user'] = np.where(
        df['number_of_users'] > 0,
        df['bandwidth_usage'] / df['number_of_users'],
        0.0
    )

    df.to_csv('data/cleaned/wifi_clean.csv', index=False)
    print(f"  Saved {len(df):,} clean rows → data/cleaned/wifi_clean.csv")
    return df


# ════════════════════════════════════════════════════════════════════════════════
# 3. ELECTRICITY
# ════════════════════════════════════════════════════════════════════════════════
def preprocess_electricity():
    print("\n[3] Preprocessing electricity...")
    df = pd.read_csv('data/raw/electricity.csv')
    print(f"  Loaded {len(df):,} rows.")
    report_missing(df, 'electricity')

    # Fill missing with rolling 3-period mean per building
    df['units_consumed'] = df.groupby('building')['units_consumed'].transform(
        lambda x: x.fillna(x.rolling(window=3, min_periods=1).mean())
    )

    # Parse timestamp
    df = parse_timestamp(df)

    # Clip negatives
    df['units_consumed'] = df['units_consumed'].clip(lower=0.0)

    # Flag anomalies BEFORE removing (used by Module 4)
    # Anomaly = > mean + 3*std per building
    df['is_anomaly'] = 0
    for bldg, group in df.groupby('building'):
        mean = group['units_consumed'].mean()
        std  = group['units_consumed'].std()
        anomaly_mask = df['building'] == bldg
        anomaly_flag = (df.loc[anomaly_mask, 'units_consumed'] >
                        mean + 3 * std).astype(int)
        df.loc[anomaly_mask, 'is_anomaly'] = anomaly_flag.values

    # Remove extreme outliers for model training
    cleaned_parts = []
    for bldg, group in df.groupby('building'):
        group = remove_outliers_iqr(group, 'units_consumed', multiplier=4.0)
        cleaned_parts.append(group)
    df = pd.concat(cleaned_parts).reset_index(drop=True)

    df.to_csv('data/cleaned/electricity_clean.csv', index=False)
    print(f"  Saved {len(df):,} clean rows → data/cleaned/electricity_clean.csv")
    return df


# ════════════════════════════════════════════════════════════════════════════════
# 4. MESS ENTRY
# ════════════════════════════════════════════════════════════════════════════════
def preprocess_mess():
    print("\n[4] Preprocessing mess entry...")
    df = pd.read_csv('data/raw/mess_entry.csv')
    print(f"  Loaded {len(df):,} rows.")
    report_missing(df, 'mess')

    # Fill missing with meal-type median
    df['number_of_students'] = df.groupby('meal_type')['number_of_students']\
        .transform(lambda x: x.fillna(x.median()))

    # Parse timestamp
    df = parse_timestamp(df)

    # Clip negatives
    df['number_of_students'] = df['number_of_students'].clip(lower=0)

    # Remove mild outliers
    df = remove_outliers_iqr(df, 'number_of_students', multiplier=3.5)

    # Add meal slot encoding
    meal_order = {'Breakfast': 0, 'Lunch': 1, 'Snacks': 2, 'Dinner': 3}
    df['meal_slot'] = df['meal_type'].map(meal_order)

    # Normalize crowd (0-1) per meal type for comparison
    for meal, group in df.groupby('meal_type'):
        max_val = group['number_of_students'].max()
        if max_val > 0:
            df.loc[df['meal_type'] == meal, 'crowd_ratio'] = \
                df.loc[df['meal_type'] == meal, 'number_of_students'] / max_val

    df.to_csv('data/cleaned/mess_clean.csv', index=False)
    print(f"  Saved {len(df):,} clean rows → data/cleaned/mess_clean.csv")
    return df


# ════════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 55)
    print("  Smart Campus — Module 2: Preprocessing")
    print("=" * 55)
    att  = preprocess_attendance()
    wifi = preprocess_wifi()
    elec = preprocess_electricity()
    mess = preprocess_mess()
    print("\nAll cleaned datasets saved in data/cleaned/")