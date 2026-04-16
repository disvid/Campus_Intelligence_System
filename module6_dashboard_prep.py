"""
MODULE 6: Dashboard Data Preparation
Smart Campus Intelligence System
Generates all dashboard-ready CSV files for Power BI / Tableau.
Run ONCE after module3 and module5 have been executed.

DEPENDENCIES:
- module2_preprocessing.py (creates cleaned CSV files)
- module3_analytics.py (creates peak_hours, daily_trends, weekly_trends, etc.)
- module5_recommendations.py (creates recommendations.csv)

OUTPUT FILES (10 total):
1. fact_electricity.csv
2. fact_wifi.csv
3. fact_mess.csv
4. fact_attendance.csv
5. fact_peak_hours.csv
6. fact_weekly_trends.csv
7. fact_daily_trends.csv
8. dim_recommendations.csv
9. fact_elec_utilization.csv
10. fact_wifi_utilization.csv
"""

import pandas as pd
import numpy as np
import os
import sys

os.makedirs('outputs/dashboard', exist_ok=True)

DAY_MAP = {0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday',
           4:'Friday', 5:'Saturday', 6:'Sunday'}

def hour_label(h):
    """Convert hour (int) to time range label (e.g., '09:00–10:00')"""
    return f"{h:02d}:00–{(h+1):02d}:00"

def check_file_exists(filepath):
    """Verify that a required input file exists"""
    if not os.path.exists(filepath):
        print(f"ERROR: Required file not found: {filepath}")
        return False
    return True


# ── 1. fact_electricity ──────────────────────────────────────────────────────
def prep_electricity():
    """
    Prepare fact_electricity table with calculated dashboard columns.
    Calculated columns: hour_label, day_name, week_type, peak_indicator
    """
    df = pd.read_csv('data/cleaned/electricity_clean.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour']      = df['timestamp'].dt.hour
    df['hour_label'] = df['hour'].apply(hour_label)
    df['day_name']   = df['day_of_week'].map(DAY_MAP)
    df['week_type']  = df['is_weekend'].map({0:'Weekday',1:'Weekend'})
    df['peak_indicator'] = pd.cut(df['units_consumed'],
                                  bins=[-np.inf,10,20,np.inf],
                                  labels=['Low','Medium','High'])
    df.to_csv('outputs/dashboard/fact_electricity.csv', index=False)
    print(f"  ✓ fact_electricity: {len(df)} rows")


# ── 2. fact_wifi ─────────────────────────────────────────────────────────────
def prep_wifi():
    """
    Prepare fact_wifi table with calculated dashboard columns.
    Calculated columns: hour_label, day_name, week_type, load_level
    """
    df = pd.read_csv('data/cleaned/wifi_clean.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour']      = df['timestamp'].dt.hour
    df['hour_label'] = df['hour'].apply(hour_label)
    df['day_name']   = df['day_of_week'].map(DAY_MAP)
    df['week_type']  = df['is_weekend'].map({0:'Weekday',1:'Weekend'})
    df['load_level'] = pd.cut(df['number_of_users'],
                               bins=[-np.inf,50,150,np.inf],
                               labels=['Low','Medium','High'])
    df.to_csv('outputs/dashboard/fact_wifi.csv', index=False)
    print(f"  ✓ fact_wifi: {len(df)} rows")


# ── 3. fact_mess ─────────────────────────────────────────────────────────────
def prep_mess():
    """
    Prepare fact_mess table with calculated dashboard columns.
    Calculated columns: hour_label, day_name, week_type, crowd_level, time_slot_label
    """
    df = pd.read_csv('data/cleaned/mess_clean.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour']      = df['timestamp'].dt.hour
    df['hour_label']      = df['hour'].apply(hour_label)
    df['day_name']         = df['day_of_week'].map(DAY_MAP)
    df['week_type']        = df['is_weekend'].map({0:'Weekday',1:'Weekend'})
    df['crowd_level']      = pd.cut(df['crowd_ratio'],
                                    bins=[-np.inf,0.3,0.6,np.inf],
                                    labels=['Low','Medium','High'])
    df['time_slot_label']  = df['meal_type'] + ' ' + df['hour_label']
    df.to_csv('outputs/dashboard/fact_mess.csv', index=False)
    print(f"  ✓ fact_mess: {len(df)} rows")


# ── 4. fact_attendance ───────────────────────────────────────────────────────
def prep_attendance():
    """
    Prepare fact_attendance table with calculated dashboard columns.
    Calculated columns: day_name, week_type
    """
    df = pd.read_csv('data/cleaned/attendance_clean.csv')
    df['date']     = pd.to_datetime(df['date'])
    df['day_name'] = df['day_of_week'].map(DAY_MAP)
    df['week_type']= df['is_weekend'].map({0:'Weekday',1:'Weekend'})
    df.to_csv('outputs/dashboard/fact_attendance.csv', index=False)
    print(f"  ✓ fact_attendance: {len(df)} rows")


# ── 5. fact_peak_hours ───────────────────────────────────────────────────────
def prep_peak_hours():
    """
    Prepare fact_peak_hours table with calculated dashboard columns.
    Calculated columns: hour_label, wifi_status, elec_status
    Source: outputs/peak_hours.csv (from module3)
    """
    df = pd.read_csv('outputs/peak_hours.csv')
    df['hour_label']   = df['hour'].apply(hour_label)
    df['wifi_status']  = df['peak_wifi'].map({True:'Peak',False:'Normal'})
    df['elec_status']  = df['peak_electricity'].map({True:'Peak',False:'Normal'})
    df.to_csv('outputs/dashboard/fact_peak_hours.csv', index=False)
    print(f"  ✓ fact_peak_hours: {len(df)} rows")


# ── 6. fact_weekly_trends ────────────────────────────────────────────────────
def prep_weekly_trends():
    """
    Prepare fact_weekly_trends table with calculated dashboard columns.
    Calculated columns: week_label
    Source: outputs/weekly_trends.csv (from module3)
    """
    df = pd.read_csv('outputs/weekly_trends.csv')
    df['week_label'] = 'Week ' + df['week'].astype(str)
    df.to_csv('outputs/dashboard/fact_weekly_trends.csv', index=False)
    print(f"  ✓ fact_weekly_trends: {len(df)} rows")


# ── 7. dim_recommendations ───────────────────────────────────────────────────
def prep_recommendations():
    """Prepare dimension table for recommendations with priority ranking"""
    df = pd.read_csv('outputs/recommendations.csv')
    df = df.reset_index()
    df = df.rename(columns={'index':'rec_id'})
    df['rec_id'] = df['rec_id'] + 1
    priority_map = {'High':1,'Medium':2,'Low':3}
    df['priority_rank'] = df['priority'].map(priority_map)
    # Extract saving amount if present in text
    df['estimated_saving'] = df['recommendation'].str.extract(r'(₹[\d,]+)')
    df['estimated_saving'] = df['estimated_saving'].fillna('—')
    df.to_csv('outputs/dashboard/dim_recommendations.csv', index=False)
    print(f"  ✓ dim_recommendations: {len(df)} rows")


# ── 8. daily_trends (already output by module3, just copy + enhance) ─────────
def prep_daily_trends():
    """
    Prepare fact_daily_trends table with calculated dashboard columns.
    Calculated columns: month_name, week_label
    Source: outputs/daily_trends.csv (from module3)
    """
    df = pd.read_csv('outputs/daily_trends.csv')
    df['date'] = pd.to_datetime(df['date'])
    df['month_name'] = df['date'].dt.strftime('%b %Y')
    df['week_label'] = 'Week ' + df['date'].dt.isocalendar().week.astype(str)
    df.to_csv('outputs/dashboard/fact_daily_trends.csv', index=False)
    print(f"  ✓ fact_daily_trends: {len(df)} rows")


# ── 9. electricity_utilization & wifi_utilization (from module3 outputs) ─────
def prep_utilization():
    """
    Copy utilization tables from module3 outputs to dashboard folder.
    Tables: electricity_utilization.csv, wifi_utilization.csv
    """
    eu = pd.read_csv('outputs/electricity_utilization.csv')
    wu = pd.read_csv('outputs/wifi_utilization.csv')
    eu.to_csv('outputs/dashboard/fact_elec_utilization.csv', index=False)
    wu.to_csv('outputs/dashboard/fact_wifi_utilization.csv', index=False)
    print(f"  ✓ fact_elec_utilization: {len(eu)} rows")
    print(f"  ✓ fact_wifi_utilization: {len(wu)} rows")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("  SMART CAMPUS INTELLIGENCE — Dashboard Data Preparation")
    print("  Module 6: Generating all dashboard-ready CSV files")
    print("="*70 + "\n")
    
    try:
        print("Generating 10 dashboard fact/dimension tables:\n")
        prep_electricity()
        prep_wifi()
        prep_mess()
        prep_attendance()
        prep_peak_hours()
        prep_weekly_trends()
        prep_recommendations()
        prep_daily_trends()
        prep_utilization()
        
        print("\n" + "="*70)
        print("  ✓ SUCCESS: All dashboard CSVs saved to outputs/dashboard/")
        print("\n  Next steps:")
        print("  1. Run the local web dashboard with: python app.py")
        print("  2. Open http://127.0.0.1:5000 in your browser")
        print("  3. Refresh the page after rerunning the pipeline")
        print("  4. Review electricity, WiFi, mess, attendance, and recommendations")
        print("  5. Use this site for all visualization and decision support")
        print("\n" + "="*70 + "\n")
        
    except FileNotFoundError as e:
        print(f"\n  ERROR: {e}")
        print(f"  Please ensure all required files exist:")
        print(f"    - data/cleaned/electricity_clean.csv")
        print(f"    - data/cleaned/wifi_clean.csv")
        print(f"    - data/cleaned/mess_clean.csv")
        print(f"    - data/cleaned/attendance_clean.csv")
        print(f"    - outputs/peak_hours.csv")
        print(f"    - outputs/weekly_trends.csv")
        print(f"    - outputs/daily_trends.csv")
        print(f"    - outputs/recommendations.csv")
        print(f"    - outputs/electricity_utilization.csv")
        print(f"    - outputs/wifi_utilization.csv")
        sys.exit(1)
    except Exception as e:
        print(f"\n  ERROR: {e}")
        sys.exit(1)