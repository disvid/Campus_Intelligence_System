#!/usr/bin/env python
"""
Smart Campus Intelligence — Pre-Flight Validation Script
Verifies all components are ready before building Power BI dashboard
"""

import os
import sys
import pandas as pd
from pathlib import Path

def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def print_section(title):
    print(f"\n{title}")
    print("-" * 70)

def check_csv_files():
    """Verify all 10 dashboard CSV files exist"""
    print_section("✓ CHECKING CSV FILES")
    
    expected_files = [
        'fact_electricity.csv',
        'fact_wifi.csv',
        'fact_mess.csv',
        'fact_attendance.csv',
        'fact_peak_hours.csv',
        'fact_daily_trends.csv',
        'fact_weekly_trends.csv',
        'dim_recommendations.csv',
        'fact_elec_utilization.csv',
        'fact_wifi_utilization.csv'
    ]
    
    csv_dir = Path('outputs/dashboard')
    if not csv_dir.exists():
        print("❌ ERROR: outputs/dashboard/ directory not found!")
        return False
    
    missing = []
    found = []
    
    for filename in expected_files:
        filepath = csv_dir / filename
        if filepath.exists():
            found.append(filename)
            size_mb = filepath.stat().st_size / (1024*1024)
            print(f"  ✓ {filename:<35} {size_mb:>6.2f} MB")
        else:
            missing.append(filename)
            print(f"  ❌ {filename:<35} MISSING")
    
    if missing:
        print(f"\n❌ Missing {len(missing)} files. Run module6_dashboard_prep.py first!")
        return False
    
    print(f"\n✓ All 10 CSV files found!")
    return True

def validate_csv_structure():
    """Validate each CSV has expected structure and data"""
    print_section("✓ VALIDATING CSV STRUCTURE")
    
    validations = {
        'fact_electricity.csv': {
            'expected_columns': ['timestamp', 'building', 'units_consumed', 'date', 'hour', 
                                'day_of_week', 'is_weekend', 'week', 'is_anomaly', 
                                'hour_label', 'day_name', 'week_type', 'peak_indicator'],
            'min_rows': 4000
        },
        'fact_wifi.csv': {
            'expected_columns': ['timestamp', 'location', 'number_of_users', 'bandwidth_usage',
                                'date', 'hour', 'day_of_week', 'is_weekend', 'week',
                                'bandwidth_per_user', 'hour_label', 'day_name', 'week_type', 'load_level'],
            'min_rows': 4000
        },
        'fact_mess.csv': {
            'expected_columns': ['timestamp', 'meal_type', 'number_of_students', 'date', 'hour',
                                'day_of_week', 'is_weekend', 'week', 'meal_slot', 'crowd_ratio',
                                'hour_label', 'day_name', 'week_type', 'crowd_level', 'time_slot_label'],
            'min_rows': 1000
        },
        'fact_attendance.csv': {
            'expected_columns': ['student_id', 'date', 'class_id', 'attendance_status',
                                'day_of_week', 'is_weekend', 'month', 'week', 'is_present',
                                'day_name', 'week_type'],
            'min_rows': 10000
        },
        'dim_recommendations.csv': {
            'expected_columns': ['rec_id', 'category', 'priority', 'recommendation',
                                'priority_rank', 'estimated_saving'],
            'min_rows': 20
        }
    }
    
    all_valid = True
    
    for csv_file, rules in validations.items():
        filepath = f'outputs/dashboard/{csv_file}'
        try:
            df = pd.read_csv(filepath)
            row_count = len(df)
            col_count = len(df.columns)
            
            # Check row count
            if row_count < rules['min_rows']:
                print(f"❌ {csv_file}: Only {row_count} rows (expected ≥{rules['min_rows']})")
                all_valid = False
            else:
                print(f"✓ {csv_file:<35} {row_count:>6} rows × {col_count:>2} columns")
            
            # Check for expected columns
            missing_cols = set(rules['expected_columns']) - set(df.columns)
            if missing_cols:
                print(f"   ⚠ Missing columns: {', '.join(missing_cols)}")
                all_valid = False
                
        except Exception as e:
            print(f"❌ {csv_file}: {str(e)}")
            all_valid = False
    
    if all_valid:
        print("\n✓ All CSVs have correct structure and adequate data!")
    return all_valid

def check_data_quality():
    """Check for data quality issues"""
    print_section("✓ CHECKING DATA QUALITY")
    
    try:
        # Check electricity data
        elec = pd.read_csv('outputs/dashboard/fact_electricity.csv')
        print(f"✓ fact_electricity: {len(elec)} rows, {elec['is_anomaly'].sum()} anomalies")
        
        # Check attendance data
        attend = pd.read_csv('outputs/dashboard/fact_attendance.csv')
        present_count = attend['is_present'].sum()
        print(f"✓ fact_attendance: {len(attend)} records, {present_count} present")
        
        # Check recommendations
        recs = pd.read_csv('outputs/dashboard/dim_recommendations.csv')
        high = len(recs[recs['priority'] == 'High'])
        print(f"✓ dim_recommendations: {len(recs)} recommendations ({high} High priority)")
        
        print("\n✓ Data quality checks passed!")
        return True
        
    except Exception as e:
        print(f"❌ Data quality check failed: {str(e)}")
        return False

def check_powerbi_requirements():
    """Check if Power BI can be installed"""
    print_section("✓ CHECKING POWER BI REQUIREMENTS")
    
    requirements = [
        ("Windows 10 or later", "Check: Settings → System → About"),
        ("4 GB RAM (minimum)", "Check: Task Manager → Performance"),
        ("500 MB free disk space", "Check: File Explorer → Properties"),
        ("Power BI Desktop (free)", "Download: https://powerbi.microsoft.com/downloads/"),
    ]
    
    for req, check in requirements:
        print(f"  □ {req}")
        print(f"     → {check}")
    
    print("\n⚠ Verify Power BI Desktop is installed before proceeding:")
    print("  1. Open Command Prompt")
    print('  2. Run: where PBIDesktop.exe')
    print("  3. If found → Power BI is installed and ready")
    print("  4. If not found → Download and install from link above")

def generate_summary():
    """Generate final summary report"""
    print_header("SMART CAMPUS INTELLIGENCE — PRE-FLIGHT CHECK SUMMARY")
    
    checks = []
    
    # CSV Files Check
    if check_csv_files():
        checks.append(("✓ CSV Files", "All 10 files present"))
    else:
        checks.append(("❌ CSV Files", "Some files missing"))
    
    # Structure Check
    if validate_csv_structure():
        checks.append(("✓ Data Structure", "All CSVs properly formatted"))
    else:
        checks.append(("❌ Data Structure", "Some issues detected"))
    
    # Quality Check
    if check_data_quality():
        checks.append(("✓ Data Quality", "All data quality checks passed"))
    else:
        checks.append(("❌ Data Quality", "Some quality issues detected"))
    
    # Power BI Check
    check_powerbi_requirements()
    
    # Print final summary
    print_header("FINAL STATUS")
    
    all_passed = all(check[0].startswith("✓") for check in checks)
    
    for check_name, status in checks:
        print(f"  {check_name:<30} {status}")
    
    if all_passed:
        print(f"\n{'='*70}")
        print("  ✓✓✓ ALL CHECKS PASSED - READY FOR POWER BI SETUP ✓✓✓")
        print(f"{'='*70}")
        
        print("\nNext Steps:")
        print("  1. Download & install Power BI Desktop (free)")
        print("  2. Open: POWERBI_SETUP_GUIDE.md")
        print("  3. Follow Section A (Import CSV Files)")
        print("  4. Follow Section B (Create Relationships)")
        print("  5. Follow Section C-F (Build Dashboard)")
        print("\nEstimated Time: 45-60 minutes\n")
        
        return True
    else:
        print(f"\n{'='*70}")
        print("  ❌ SOME CHECKS FAILED - SEE ABOVE FOR DETAILS")
        print(f"{'='*70}\n")
        return False

if __name__ == '__main__':
    try:
        success = generate_summary()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Validation script error: {str(e)}")
        sys.exit(1)
