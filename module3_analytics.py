"""
MODULE 3: Analytics
Smart Campus Intelligence System
Computes peak hours, daily/weekly trends, and resource utilization.
Saves output CSVs to outputs/ for dashboard use.
"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

os.makedirs('outputs', exist_ok=True)
os.makedirs('outputs/plots', exist_ok=True)


# ─── Loader helpers ───────────────────────────────────────────────────────────
def load_wifi():
    df = pd.read_csv('data/cleaned/wifi_clean.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date   # ✅ ADD THIS
    df['hour'] = df['timestamp'].dt.hour   # (you already use hour)
    return df

def load_electricity():
    df = pd.read_csv('data/cleaned/electricity_clean.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date   # ✅ ADD THIS
    df['hour'] = df['timestamp'].dt.hour
    return df

def load_mess():
    df = pd.read_csv('data/cleaned/mess_clean.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date   # ✅ ADD THIS
    df['hour'] = df['timestamp'].dt.hour
    return df

def load_attendance():
    df = pd.read_csv('data/cleaned/attendance_clean.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df


# ════════════════════════════════════════════════════════════════════════════════
# A. PEAK HOURS ANALYSIS
# ════════════════════════════════════════════════════════════════════════════════
def analyze_peak_hours(wifi_df, elec_df, mess_df):
    print("\n[A] Computing peak hours...")

    # WiFi peak hours (avg users per hour across all locations)
    wifi_peak = (wifi_df.groupby('hour')['number_of_users']
                 .mean()
                 .reset_index()
                 .rename(columns={'number_of_users': 'avg_wifi_users'}))
    wifi_peak['peak_wifi'] = wifi_peak['avg_wifi_users'] > \
        wifi_peak['avg_wifi_users'].quantile(0.75)

    # Electricity peak hours (avg units across all buildings)
    elec_peak = (elec_df.groupby('hour')['units_consumed']
                 .mean()
                 .reset_index()
                 .rename(columns={'units_consumed': 'avg_units'}))
    elec_peak['peak_electricity'] = elec_peak['avg_units'] > \
        elec_peak['avg_units'].quantile(0.75)

    # Mess peak slots (avg students per meal_type per hour)
    mess_peak = (mess_df.groupby(['meal_type', 'hour'])['number_of_students']
                 .mean()
                 .reset_index()
                 .rename(columns={'number_of_students': 'avg_students'}))

    # Combined peak hours table
    peak_combined = wifi_peak.merge(elec_peak, on='hour')
    peak_combined.to_csv('outputs/peak_hours.csv', index=False)
    mess_peak.to_csv('outputs/mess_peak_hours.csv', index=False)

    top_wifi  = wifi_peak.nlargest(3, 'avg_wifi_users')['hour'].tolist()
    top_elec  = elec_peak.nlargest(3, 'avg_units')['hour'].tolist()
    print(f"  Top WiFi peak hours   : {top_wifi}")
    print(f"  Top electricity hours : {top_elec}")
    return peak_combined, mess_peak


# ════════════════════════════════════════════════════════════════════════════════
# B. DAILY TRENDS
# ════════════════════════════════════════════════════════════════════════════════
def analyze_daily_trends(wifi_df, elec_df, mess_df, att_df):
    print("\n[B] Computing daily trends...")

    # Daily WiFi users
    wifi_daily = (wifi_df.groupby('date')['number_of_users']
                  .sum()
                  .reset_index()
                  .rename(columns={'date': 'date', 'number_of_users': 'total_wifi_users'}))

    # Daily electricity
    elec_daily = (elec_df.groupby('date')['units_consumed']
                  .sum()
                  .reset_index()
                  .rename(columns={'date': 'date', 'units_consumed': 'total_units'}))

    # Daily mess entries
    mess_daily = (mess_df.groupby('date')['number_of_students']
                  .sum()
                  .reset_index()
                  .rename(columns={'date': 'date', 'number_of_students': 'total_mess_entries'}))

    # Daily attendance rate
    att_daily = (att_df.groupby('date')['is_present']
                 .mean()
                 .reset_index()
                 .rename(columns={'is_present': 'attendance_rate'}))
    att_daily['attendance_rate'] = (att_daily['attendance_rate'] * 100).round(2)

    # Ensure all date columns are datetime
    wifi_daily['date'] = pd.to_datetime(wifi_daily['date'])
    elec_daily['date'] = pd.to_datetime(elec_daily['date'])
    mess_daily['date'] = pd.to_datetime(mess_daily['date'])
    att_daily['date']  = pd.to_datetime(att_daily['date'])
    
    # Merge all
    daily = (wifi_daily
             .merge(elec_daily, on='date', how='outer')
             .merge(mess_daily, on='date', how='outer')
             .merge(att_daily, on='date', how='outer'))
    daily['date'] = pd.to_datetime(daily['date'])
    daily.sort_values('date', inplace=True)
    daily['day_name'] = daily['date'].dt.day_name()
    daily['is_weekend'] = daily['date'].dt.dayofweek.apply(
        lambda x: 'Weekend' if x >= 5 else 'Weekday'
    )

    daily.to_csv('outputs/daily_trends.csv', index=False)
    print(f"  Saved {len(daily)} daily records → outputs/daily_trends.csv")
    return daily


# ════════════════════════════════════════════════════════════════════════════════
# C. WEEKLY TRENDS
# ════════════════════════════════════════════════════════════════════════════════
def analyze_weekly_trends(daily_df):
    print("\n[C] Computing weekly trends...")
    daily_df['week'] = pd.to_datetime(daily_df['date']).dt.isocalendar().week
    weekly = daily_df.groupby('week').agg(
        avg_wifi_users    = ('total_wifi_users',   'mean'),
        avg_units         = ('total_units',         'mean'),
        avg_mess_entries  = ('total_mess_entries',  'mean'),
        avg_attendance    = ('attendance_rate',      'mean')
    ).reset_index()
    weekly.to_csv('outputs/weekly_trends.csv', index=False)
    print(f"  Saved {len(weekly)} weekly records → outputs/weekly_trends.csv")
    return weekly


# ════════════════════════════════════════════════════════════════════════════════
# D. RESOURCE UTILIZATION PER BUILDING / LOCATION
# ════════════════════════════════════════════════════════════════════════════════
def analyze_utilization(wifi_df, elec_df):
    print("\n[D] Computing resource utilization...")

    # WiFi utilization per location
    wifi_util = wifi_df.groupby('location').agg(
        total_users      = ('number_of_users', 'sum'),
        avg_users_per_hr = ('number_of_users', 'mean'),
        max_users        = ('number_of_users', 'max'),
        total_bandwidth  = ('bandwidth_usage', 'sum')
    ).reset_index()
    wifi_util['utilization_pct'] = (
        wifi_util['avg_users_per_hr'] / wifi_util['avg_users_per_hr'].max() * 100
    ).round(2)

    # Electricity per building
    elec_util = elec_df.groupby('building').agg(
        total_units      = ('units_consumed', 'sum'),
        avg_hourly_units = ('units_consumed', 'mean'),
        max_units        = ('units_consumed', 'max')
    ).reset_index()
    elec_util['energy_share_pct'] = (
        elec_util['total_units'] / elec_util['total_units'].sum() * 100
    ).round(2)

    wifi_util.to_csv('outputs/wifi_utilization.csv', index=False)
    elec_util.to_csv('outputs/electricity_utilization.csv', index=False)
    print("  Saved → outputs/wifi_utilization.csv")
    print("  Saved → outputs/electricity_utilization.csv")
    return wifi_util, elec_util


# ════════════════════════════════════════════════════════════════════════════════
# E. VISUALIZATIONS
# ════════════════════════════════════════════════════════════════════════════════
def create_visualizations(peak_df, daily_df, wifi_util, elec_util):
    print("\n[E] Generating plots...")
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Smart Campus — Analytics Dashboard', fontsize=16, fontweight='bold')

    # 1. WiFi users by hour
    ax = axes[0, 0]
    ax.bar(peak_df['hour'], peak_df['avg_wifi_users'],
           color=['#e74c3c' if p else '#3498db'
                  for p in peak_df['peak_wifi']])
    ax.set_title('Avg WiFi Users by Hour')
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Avg Users')
    ax.set_xticks(range(0, 24, 2))

    # 2. Electricity by hour
    ax = axes[0, 1]
    ax.bar(peak_df['hour'], peak_df['avg_units'],
           color=['#e74c3c' if p else '#2ecc71'
                  for p in peak_df['peak_electricity']])
    ax.set_title('Avg Electricity by Hour')
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Units Consumed')
    ax.set_xticks(range(0, 24, 2))

    # 3. Daily trends - electricity
    ax = axes[0, 2]
    dates = pd.to_datetime(daily_df['date'])
    ax.plot(dates, daily_df['total_units'], color='#e67e22', linewidth=2)
    ax.fill_between(dates, daily_df['total_units'], alpha=0.2, color='#e67e22')
    ax.set_title('Daily Electricity Consumption')
    ax.set_xlabel('Date')
    ax.set_ylabel('Total Units')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30)

    # 4. WiFi utilization by location
    ax = axes[1, 0]
    ax.barh(wifi_util['location'], wifi_util['utilization_pct'],
            color='#3498db')
    ax.set_title('WiFi Utilization by Location')
    ax.set_xlabel('Utilization %')
    ax.set_xlim(0, 110)
    for i, v in enumerate(wifi_util['utilization_pct']):
        ax.text(v + 1, i, f'{v:.1f}%', va='center', fontsize=9)

    # 5. Electricity share by building
    ax = axes[1, 1]
    ax.pie(elec_util['energy_share_pct'],
           labels=elec_util['building'],
           autopct='%1.1f%%',
           startangle=90,
           colors=['#e74c3c', '#e67e22', '#f1c40f',
                   '#2ecc71', '#3498db', '#9b59b6'])
    ax.set_title('Electricity Share by Building')

    # 6. Daily WiFi users trend
    ax = axes[1, 2]
    weekday_mask = daily_df['is_weekend'] == 'Weekday'
    weekend_mask = daily_df['is_weekend'] == 'Weekend'
    ax.scatter(pd.to_datetime(daily_df.loc[weekday_mask, 'date']),
               daily_df.loc[weekday_mask, 'total_wifi_users'],
               label='Weekday', color='#3498db', s=40)
    ax.scatter(pd.to_datetime(daily_df.loc[weekend_mask, 'date']),
               daily_df.loc[weekend_mask, 'total_wifi_users'],
               label='Weekend', color='#e74c3c', s=40)
    ax.set_title('Daily WiFi Users')
    ax.set_xlabel('Date')
    ax.set_ylabel('Total Users')
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30)

    plt.tight_layout()
    plt.savefig('outputs/plots/analytics_dashboard.png', dpi=150,
                bbox_inches='tight')
    print("  Plot saved → outputs/plots/analytics_dashboard.png")
    plt.close()


# ════════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 55)
    print("  Smart Campus — Module 3: Analytics")
    print("=" * 55)

    wifi_df = load_wifi()
    elec_df = load_electricity()
    mess_df = load_mess()
    att_df  = load_attendance()

    peak_df, mess_peak   = analyze_peak_hours(wifi_df, elec_df, mess_df)
    daily_df             = analyze_daily_trends(wifi_df, elec_df,
                                                mess_df, att_df)
    weekly_df            = analyze_weekly_trends(daily_df)
    wifi_util, elec_util = analyze_utilization(wifi_df, elec_df)
    create_visualizations(peak_df, daily_df, wifi_util, elec_util)

    print("\nAll analytics outputs saved in outputs/")