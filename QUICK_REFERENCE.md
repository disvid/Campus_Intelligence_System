# Smart Campus Intelligence — Quick Reference Card

## 10 Dashboard-Ready CSV Files

| # | File | Rows | Primary Key | Key Calculated Columns |
|---|------|------|-------------|------------------------|
| 1 | **fact_electricity** | 4,455 | timestamp, building | hour_label, peak_indicator, day_name, week_type |
| 2 | **fact_wifi** | 4,458 | timestamp, location | hour_label, load_level, day_name, week_type |
| 3 | **fact_mess** | 1,302 | timestamp, meal_type | hour_label, crowd_level, time_slot_label, day_name |
| 4 | **fact_attendance** | 16,745 | date, student_id | day_name, week_type |
| 5 | **fact_peak_hours** | 24 | hour | hour_label, wifi_status, elec_status |
| 6 | **fact_daily_trends** | 31 | date | week_label, month_name |
| 7 | **fact_weekly_trends** | 5 | week | week_label |
| 8 | **fact_elec_utilization** | 6 | building | (no additional columns) |
| 9 | **fact_wifi_utilization** | 6 | location | (no additional columns) |
| 10 | **dim_recommendations** | 27 | rec_id | priority_rank, estimated_saving |

## Table Relationships

```
fact_daily_trends[date]      →  fact_electricity[date]        (1:M)
fact_daily_trends[date]      →  fact_wifi[date]               (1:M)
fact_daily_trends[date]      →  fact_mess[date]               (1:M)
fact_daily_trends[date]      →  fact_attendance[date]         (1:M)
fact_peak_hours[hour]        →  fact_electricity[hour]        (1:M)
fact_peak_hours[hour]        →  fact_wifi[hour]               (1:M)
fact_weekly_trends[week]     →  fact_daily_trends[week]       (1:M)
dim_recommendations[rec_id]  →  (standalone, no relations)    (—)
```

## Essential Measures (DAX / Calculated Fields)

### KPIs
```dax
Avg Electricity (kWh) = AVERAGE(fact_electricity[units_consumed])
Peak Mess Hour = FORMAT(VAR hour = CALCULATE(...), "00") & ":00"
Max WiFi Users = MAX(fact_wifi[number_of_users])
Avg Attendance % = AVERAGE(fact_daily_trends[attendance_rate])
```

### Analytics
```dax
Energy Share % = DIVIDE(SUM(...), CALCULATE(SUM(...), ALL(...))) * 100
WiFi Utilization % = DIVIDE(AVERAGE(...), MAX(...), ALL(...))) * 100
Attendance Rate % = DIVIDE(SUM(is_present), COUNT(student_id)) * 100
Anomaly Count = CALCULATE(COUNT(is_anomaly), is_anomaly = 1)
```

## 6 Dashboard Pages Structure

| Page | Main Visuals | Key Slicers |
|------|-------------|-------------|
| **1. Overview** | 4 KPIs + Line Chart (daily elec) | Date Range |
| **2. Resource Utilization** | 2 Bar Charts + Pie Chart | Building, Location |
| **3. Peak Hours Analysis** | Heatmap + 2 Line Charts | Hour, Day Type |
| **4. Predictive Insights** | 2 Multi-line Area Charts | Week Range |
| **5. Anomaly Detection** | Scatter + Table + KPI | Anomaly Flag |
| **6. Recommendations** | Table with conditional formatting | Category, Priority |

## Color Palette

### Status Colors
| Status | Hex | RGB |
|--------|-----|-----|
| High/Alert (Red) | #E74C3C | 231, 76, 60 |
| Medium (Orange) | #E67E22 | 230, 126, 34 |
| Low/Safe (Green) | #2ECC71 | 46, 204, 113 |
| Info (Blue) | #3498DB | 52, 152, 219 |
| Neutral (Grey) | #95A5A6 | 149, 165, 166 |

### Building Colors (Use Consistently)
- **Academic Block A** → #3498DB (Blue)
- **Academic Block B** → #2980B9 (Dark Blue)
- **Hostel Block 1** → #E74C3C (Red)
- **Hostel Block 2** → #C0392B (Dark Red)
- **Library** → #9B59B6 (Purple)
- **Sports Complex** → #1ABC9C (Teal)
- **Cafeteria/Mess** → #E67E22 (Orange)

### Priority Colors (Recommendations)
- **High** → BG: #FADBD8 | Text: #E74C3C
- **Medium** → BG: #FDEBD0 | Text: #E67E22
- **Low** → BG: #D5F5E3 | Text: #27AE60

## Conditional Formatting Rules

### Peak Indicator (Electricity)
```
IF value = "High"   → #E74C3C (red)
IF value = "Medium" → #E67E22 (orange)
IF value = "Low"    → #2ECC71 (green)
```

### Load Level (WiFi)
```
High    (>150 users) → #E74C3C (red)
Medium  (50-150)     → #E67E22 (orange)
Low     (<50)        → #2ECC71 (green)
```

### Crowd Level (Mess)
```
High    (ratio > 0.6)  → #E74C3C (red)
Medium  (0.3 - 0.6)    → #E67E22 (orange)
Low     (ratio < 0.3)  → #2ECC71 (green)
```

### Heatmap (WiFi Hour × Day)
```
0-50 users   → #2ECC71 (green)
51-150       → #E67E22 (orange)
151+         → #E74C3C (red)
```

## Column Data Types Checklist

| Column Type | Format | Example |
|------------|--------|---------|
| Date | Date | 2024-03-01 |
| Timestamp | Date & Time | 2024-03-01 09:00:00 |
| Hour | Whole Number | 9 |
| Week | Whole Number | 9 |
| Units Consumed | Decimal | 41.684 |
| Number of Users | Whole Number | 359 |
| Bandwidth Usage | Decimal | 531.01 |
| Crowd Ratio | Decimal | 0.643 |
| Is Present | Whole Number | 1 or 0 |
| Is Anomaly | Whole Number | 0 or 1 |
| Building/Location | Text | "Academic Block A" |

## Slicer Configuration

### Date Range Slicer
- Field: `fact_daily_trends[date]`
- Type: Between (date range picker)
- Apply to: All time-based charts

### Building Slicer
- Field: `fact_electricity[building]`
- Type: Multiple select (list)
- Apply to: Electricity & utilization visuals

### Location Slicer
- Field: `fact_wifi[location]`
- Type: Multiple select (list)
- Apply to: WiFi & utilization visuals

### Week Type Slicer
- Field: `fact_electricity[week_type]`
- Type: Single select (buttons)
- Values: Weekday / Weekend

### Hour Slicer
- Field: `fact_peak_hours[hour_label]`
- Type: Multiple select (dropdown)
- Format: "HH:00–HH:00"

### Category Slicer (Recommendations)
- Field: `dim_recommendations[category]`
- Type: Tiles (horizontal buttons)

### Priority Slicer (Recommendations)
- Field: `dim_recommendations[priority]`
- Type: Dropdown
- Values: High / Medium / Low

## Power BI Settings

**Page Size:** 1280 × 720 (Custom)  
**Theme Color Scheme:**
- Background: #F8F9FA
- Card Background: #FFFFFF
- Primary Accent: #2C3E50
- Header: #2C3E50 (dark navy)
- Text: #2C3E50

**Typography:**
- Titles: Segoe UI Semibold, 14pt
- Labels: Segoe UI, 10pt
- Card Values: Segoe UI Bold, 24pt

## Calculated Field Formulas (Tableau)

```
Hour Label = STR(INT([Hour])) + ":00–" + STR(INT([Hour])+1) + ":00"

Day Name = DATENAME('weekday', [Date])

Week Type = IF DATEPART('weekday',[Date]) >= 6 
            THEN "Weekend" ELSE "Weekday" END

Peak Indicator = IF [Units Consumed] > 20 THEN "High"
                ELSEIF [Units Consumed] > 10 THEN "Medium"
                ELSE "Low" END

Crowd Level = IF [Crowd Ratio] > 0.6 THEN "High"
             ELSEIF [Crowd Ratio] > 0.3 THEN "Medium"
             ELSE "Low" END

Attendance Rate % = AVG([Is Present]) * 100

Energy Share % = SUM([Units Consumed]) / 
                TOTAL(SUM([Units Consumed])) * 100
```

## Troubleshooting Quick Fixes

| Issue | Solution |
|-------|----------|
| Relationships not working | Verify tables imported, date columns are Date type |
| DAX formula error | Check column/table names (case-sensitive), syntax |
| Slicers not filtering | Enable "Sync Slicers", verify relationships exist |
| Empty anomaly page | Check `is_anomaly = 1` filter, verify data exists |
| Performance slow | Reduce date range, use DirectQuery, aggregate data |
| Charts show wrong colors | Verify conditional formatting rules applied |
| Numbers misaligned | Check decimal/whole number types for calculations |

## Data Validation Checklist

Before publishing dashboard:
- [ ] All 10 CSVs imported successfully
- [ ] All relationships created (7 total)
- [ ] All measures calculated without errors
- [ ] Slicers cross-filtering correctly
- [ ] Date range covers full data span
- [ ] Building/location values match data
- [ ] Colors applied per design spec
- [ ] No #ERROR or blank results
- [ ] Charts display expected trends
- [ ] Recommendations table sorted by priority

## Installation Steps (Quick)

```bash
# 1. Ensure modules 2-5 have been executed
python module2_preprocessing.py
python module3_analytics.py
python module5_recommendations.py

# 2. Generate dashboard CSVs
python module6_dashboard_prep.py

# 3. Open Power BI or Tableau Desktop
# 4. Import all 10 CSVs from outputs/dashboard/
# 5. Follow DASHBOARD_GUIDE.md for detailed setup
```

---

**Print this card and keep it handy while building your dashboard!**

*v1.0 — Smart Campus Intelligence System*  
*April 2026*
