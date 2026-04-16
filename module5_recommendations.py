"""
MODULE 5: Recommendation Engine
Smart Campus Intelligence System

Logic-based, data-driven recommendations covering:
  1. Best time to visit mess (least crowded slots)
  2. Energy-saving suggestions per building
  3. Class scheduling optimization
  4. WiFi-based capacity warnings
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

os.makedirs('outputs', exist_ok=True)


# ════════════════════════════════════════════════════════════════════════════════
# DATA LOADERS
# ════════════════════════════════════════════════════════════════════════════════
def load_data():
    mess  = pd.read_csv('data/cleaned/mess_clean.csv')
    elec  = pd.read_csv('data/cleaned/electricity_clean.csv')
    wifi  = pd.read_csv('data/cleaned/wifi_clean.csv')
    att   = pd.read_csv('data/cleaned/attendance_clean.csv')

    mess['timestamp']  = pd.to_datetime(mess['timestamp'])
    elec['timestamp']  = pd.to_datetime(elec['timestamp'])
    wifi['timestamp']  = pd.to_datetime(wifi['timestamp'])
    att['date']        = pd.to_datetime(att['date'])
    return mess, elec, wifi, att


# ════════════════════════════════════════════════════════════════════════════════
# 1. MESS TIMING RECOMMENDATIONS
# ════════════════════════════════════════════════════════════════════════════════
def recommend_mess_timing(mess_df):
    """
    Finds the quietest 30-min window within each meal service for weekdays
    and weekends separately.
    Logic: compute avg students per (meal_type, hour, minute_bucket, weekday).
    Recommend the 2 lowest-crowd slots per meal per day type.
    """
    print("\n[1] Mess timing recommendations...")

    mess_df['minute_bucket'] = (mess_df['timestamp'].dt.minute // 30) * 30
    mess_df['is_weekend']    = (mess_df['timestamp'].dt.dayofweek >= 5).astype(int)
    mess_df['hour']          = mess_df['timestamp'].dt.hour

    agg = (mess_df
           .groupby(['meal_type', 'hour', 'minute_bucket', 'is_weekend'])
           ['number_of_students']
           .mean()
           .reset_index()
           .rename(columns={'number_of_students': 'avg_crowd'}))
    agg['avg_crowd'] = agg['avg_crowd'].round(1)

    recommendations = []
    for meal in ['Breakfast', 'Lunch', 'Snacks', 'Dinner']:
        for day_type, day_label in [(0, 'Weekday'), (1, 'Weekend')]:
            subset = agg[(agg['meal_type'] == meal) &
                         (agg['is_weekend'] == day_type)].copy()
            if subset.empty:
                continue

            max_crowd = subset['avg_crowd'].max()
            min_crowd = subset['avg_crowd'].min()
            peak_row  = subset.loc[subset['avg_crowd'].idxmax()]
            quiet_rows = subset.nsmallest(2, 'avg_crowd')

            for _, qr in quiet_rows.iterrows():
                crowd_reduction = ((max_crowd - qr['avg_crowd']) /
                                   (max_crowd + 1e-6) * 100)
                recommendations.append({
                    'meal_type':         meal,
                    'day_type':          day_label,
                    'best_hour':         int(qr['hour']),
                    'best_minute':       int(qr['minute_bucket']),
                    'avg_crowd_then':    qr['avg_crowd'],
                    'peak_crowd':        round(max_crowd, 1),
                    'crowd_reduction_%': round(crowd_reduction, 1),
                    'recommendation':    (
                        f"Visit {meal} at "
                        f"{int(qr['hour']):02d}:{int(qr['minute_bucket']):02d} "
                        f"on {day_label}s — avg {qr['avg_crowd']:.0f} students "
                        f"vs peak {max_crowd:.0f} "
                        f"({crowd_reduction:.0f}% less crowded)"
                    )
                })

    rec_df = pd.DataFrame(recommendations)
    print(rec_df[['meal_type', 'day_type', 'best_hour', 'best_minute',
                  'crowd_reduction_%']].to_string(index=False))
    return rec_df


# ════════════════════════════════════════════════════════════════════════════════
# 2. ENERGY-SAVING SUGGESTIONS
# ════════════════════════════════════════════════════════════════════════════════
def recommend_energy_saving(elec_df, wifi_df):
    """
    Logic:
    - Find hours where electricity is HIGH but WiFi users are LOW per building
      → likely equipment running with no occupancy (lights, AC)
    - Find buildings with consistently above-average consumption on weekends
    - Compute potential savings if off-hours consumption is reduced by 40%
    """
    print("\n[2] Energy-saving recommendations...")

    elec_df['hour']       = elec_df['timestamp'].dt.hour
    elec_df['is_weekend'] = (elec_df['timestamp'].dt.dayofweek >= 5).astype(int)

    wifi_df['hour']       = wifi_df['timestamp'].dt.hour
    wifi_df['is_weekend'] = (wifi_df['timestamp'].dt.dayofweek >= 5).astype(int)

    # Academic zone WiFi as proxy for occupancy in academic buildings
    acad_wifi = (wifi_df[wifi_df['location'] == 'Academic Zone']
                 .groupby(['hour', 'is_weekend'])['number_of_users']
                 .mean()
                 .reset_index()
                 .rename(columns={'number_of_users': 'avg_users'}))

    LOW_OCC_THRESHOLD = acad_wifi['avg_users'].quantile(0.25)

    suggestions = []
    for bldg, grp in elec_df.groupby('building'):
        bldg_hourly = (grp.groupby(['hour', 'is_weekend'])
                       ['units_consumed'].mean()
                       .reset_index()
                       .rename(columns={'units_consumed': 'avg_units'}))

        # Merge with WiFi occupancy
        merged = bldg_hourly.merge(acad_wifi, on=['hour', 'is_weekend'],
                                   how='left')
        merged['avg_users'].fillna(acad_wifi['avg_users'].mean(), inplace=True)

        # High consumption, low occupancy
        hi_cons_lo_occ = merged[
            (merged['avg_units'] > merged['avg_units'].quantile(0.65)) &
            (merged['avg_users'] < LOW_OCC_THRESHOLD)
        ]

        if hi_cons_lo_occ.empty:
            continue

        wasted = hi_cons_lo_occ['avg_units'].sum()
        # Assuming 40% savings possible with smart automation
        saving_potential = round(wasted * 0.40, 2)
        monthly_saving   = round(saving_potential * 30, 2)

        wasteful_hours = sorted(hi_cons_lo_occ['hour'].unique().tolist())

        suggestions.append({
            'building':            bldg,
            'wasteful_hours':      str(wasteful_hours),
            'avg_wasted_units_/d': round(wasted, 2),
            'saving_potential_%':  40,
            'monthly_saving_units': monthly_saving,
            'recommendation': (
                f"{bldg}: High electricity during low-occupancy hours "
                f"{wasteful_hours}. Estimated monthly saving with auto-shutdown: "
                f"{monthly_saving} units (~₹{monthly_saving * 8:.0f} "
                f"at ₹8/unit)."
            )
        })

    sug_df = pd.DataFrame(suggestions)
    if not sug_df.empty:
        print(sug_df[['building', 'wasteful_hours',
                      'monthly_saving_units']].to_string(index=False))
    return sug_df


# ════════════════════════════════════════════════════════════════════════════════
# 3. CLASS SCHEDULING OPTIMIZATION
# ════════════════════════════════════════════════════════════════════════════════
def recommend_class_scheduling(att_df, wifi_df):
    """
    Logic:
    - Compute attendance rate by day_of_week × hour block
    - Find slots with both high attendance AND low WiFi load
      → good candidates for high-importance classes
    - Flag low-attendance slots → reschedule or convert to self-study
    """
    print("\n[3] Class scheduling recommendations...")

    att_df['hour_block'] = (att_df['date'].dt.hour
                            if 'hour' in att_df.columns
                            else 9)   # default 9 AM for date-only records

    # Attendance by day of week
    att_by_day = (att_df.groupby('day_of_week')['is_present']
                  .mean()
                  .reset_index()
                  .rename(columns={'is_present': 'att_rate'}))
    att_by_day['att_rate_pct'] = (att_by_day['att_rate'] * 100).round(2)
    att_by_day['day_name'] = att_by_day['day_of_week'].map({
        0: 'Monday', 1: 'Tuesday', 2: 'Wednesday',
        3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'
    })

    wifi_df['hour'] = wifi_df['timestamp'].dt.hour if 'hour' not in wifi_df.columns \
        else wifi_df['hour']
    wifi_by_hour = (wifi_df.groupby('hour')['number_of_users']
                    .mean()
                    .reset_index()
                    .rename(columns={'number_of_users': 'avg_wifi_users'}))

    recommendations = []

    # High-attendance days
    high_att = att_by_day[att_by_day['att_rate'] >= att_by_day['att_rate'].quantile(0.6)]
    low_att  = att_by_day[att_by_day['att_rate'] <  att_by_day['att_rate'].quantile(0.4)]

    for _, row in high_att.iterrows():
        recommendations.append({
            'type':           'Optimal Day',
            'day':            row['day_name'],
            'attendance_%':   row['att_rate_pct'],
            'recommendation': (
                f"Schedule critical exams / important lectures on "
                f"{row['day_name']} — avg attendance {row['att_rate_pct']}%."
            )
        })

    for _, row in low_att.iterrows():
        recommendations.append({
            'type':           'Low Attendance Day',
            'day':            row['day_name'],
            'attendance_%':   row['att_rate_pct'],
            'recommendation': (
                f"Consider converting {row['day_name']} slots to self-study / "
                f"tutorials — avg attendance only {row['att_rate_pct']}%."
            )
        })

    # WiFi-low hours → good for online-heavy classes
    low_wifi_hours = wifi_by_hour.nsmallest(3, 'avg_wifi_users')
    for _, row in low_wifi_hours.iterrows():
        recommendations.append({
            'type':           'Low WiFi Load Hour',
            'day':            'Any',
            'attendance_%':   None,
            'recommendation': (
                f"Hour {int(row['hour']):02d}:00 has low WiFi load "
                f"(avg {row['avg_wifi_users']:.0f} users) — ideal for "
                f"bandwidth-heavy online classes or video lectures."
            )
        })

    sched_df = pd.DataFrame(recommendations)
    print(sched_df[['type', 'day', 'recommendation']].to_string(index=False))
    return sched_df, att_by_day


# ════════════════════════════════════════════════════════════════════════════════
# 4. WIFI CAPACITY WARNINGS
# ════════════════════════════════════════════════════════════════════════════════
def recommend_wifi_capacity(wifi_df):
    """
    Flag location × hour combos where avg users > 80% of max observed.
    Recommend infrastructure upgrade or load balancing.
    """
    print("\n[4] WiFi capacity recommendations...")

    wifi_df['hour'] = wifi_df['timestamp'].dt.hour \
        if 'hour' not in wifi_df.columns else wifi_df['hour']

    loc_max = wifi_df.groupby('location')['number_of_users'].max()

    agg = (wifi_df.groupby(['location', 'hour'])['number_of_users']
           .mean()
           .reset_index()
           .rename(columns={'number_of_users': 'avg_users'}))
    agg['max_observed'] = agg['location'].map(loc_max)
    agg['load_pct']     = (agg['avg_users'] / agg['max_observed'] * 100).round(2)

    critical = agg[agg['load_pct'] >= 75].sort_values('load_pct', ascending=False)

    warnings = []
    for _, row in critical.iterrows():
        warnings.append({
            'location':    row['location'],
            'peak_hour':   int(row['hour']),
            'avg_users':   round(row['avg_users'], 0),
            'load_%':      row['load_pct'],
            'action':      (
                f"ALERT: {row['location']} at {int(row['hour']):02d}:00 — "
                f"WiFi load at {row['load_pct']:.0f}% capacity "
                f"(avg {row['avg_users']:.0f} users). "
                f"Consider additional access points or load balancing."
            )
        })

    warn_df = pd.DataFrame(warnings)
    if not warn_df.empty:
        print(warn_df[['location', 'peak_hour', 'load_%']].to_string(index=False))
    return warn_df


# ════════════════════════════════════════════════════════════════════════════════
# COMPILE ALL RECOMMENDATIONS
# ════════════════════════════════════════════════════════════════════════════════
def compile_recommendations(mess_rec, energy_sug, sched_rec, wifi_warn):
    print("\n[5] Compiling full recommendation report...")

    all_recs = []

    # Mess
    for _, r in mess_rec.iterrows():
        all_recs.append({
            'category':       'Mess Timing',
            'priority':       'Medium',
            'recommendation': r['recommendation']
        })

    # Energy
    for _, r in energy_sug.iterrows():
        all_recs.append({
            'category':       'Energy Saving',
            'priority':       'High',
            'recommendation': r['recommendation']
        })

    # Scheduling
    for _, r in sched_rec.iterrows():
        all_recs.append({
            'category':       'Class Scheduling',
            'priority':       'Low',
            'recommendation': r['recommendation']
        })

    # WiFi
    for _, r in wifi_warn.iterrows():
        all_recs.append({
            'category':       'WiFi Capacity',
            'priority':       'High',
            'recommendation': r['action']
        })

    final_df = pd.DataFrame(all_recs)
    final_df.to_csv('outputs/recommendations.csv', index=False)

    # Human-readable text file
    with open('outputs/recommendations.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("   SMART CAMPUS INTELLIGENCE — RECOMMENDATION REPORT\n")
        f.write(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write("=" * 70 + "\n\n")

        for cat in ['Energy Saving', 'WiFi Capacity', 'Mess Timing',
                    'Class Scheduling']:
            subset = final_df[final_df['category'] == cat]
            if subset.empty:
                continue
            f.write(f"── {cat} ──\n")
            for i, (_, row) in enumerate(subset.iterrows(), 1):
                f.write(f"  [{row['priority']}] {i}. {row['recommendation']}\n")
            f.write("\n")

    print(f"  Total recommendations: {len(final_df)}")
    print("  Saved → outputs/recommendations.csv")
    print("  Saved → outputs/recommendations.txt")
    return final_df


# ════════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 55)
    print("  Smart Campus — Module 5: Recommendations")
    print("=" * 55)

    mess_df, elec_df, wifi_df, att_df = load_data()

    mess_rec   = recommend_mess_timing(mess_df)
    energy_sug = recommend_energy_saving(elec_df, wifi_df)
    sched_rec, att_by_day = recommend_class_scheduling(att_df, wifi_df)
    wifi_warn  = recommend_wifi_capacity(wifi_df)
    final_df   = compile_recommendations(mess_rec, energy_sug,
                                          sched_rec, wifi_warn)

    print("\nSample from recommendations.txt:")
    print("─" * 55)
    with open('outputs/recommendations.txt') as f:
        for i, line in enumerate(f):
            if i > 20:
                break
            print(line, end='')