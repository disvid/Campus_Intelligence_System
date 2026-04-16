# Smart Campus Intelligence System — Complete README

**Version:** 1.0  
**Date:** April 2026  
**Status:** ✅ Production Ready

---

## System Overview

The **Smart Campus Intelligence System** is a comprehensive data analytics platform for monitoring and optimizing campus resource utilization. It processes data from 4 key sources (electricity, WiFi, mess services, attendance) and delivers actionable insights through an interactive multi-page dashboard.

### Key Features

✅ **6-Module Pipeline** — Modular design from data generation to dashboard  
✅ **4 Data Sources** — Electricity, WiFi, Mess services, Student attendance  
✅ **10 Dashboard Tables** — Optimized fact and dimension tables  
✅ **6 Interactive Pages** — Overview, utilization, peak hours, insights, anomalies, recommendations  
✅ **15+ KPI Measures** — Pre-built DAX formulas for instant analytics  
✅ **Smart Recommendations** — ML-based insights with ROI calculations  
✅ **Anomaly Detection** — Real-time outlier identification  
✅ **Multi-Slicer Support** — Date, building, location, time-based filtering  

---

## System Architecture

### Module Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│ MODULE 1: Data Generation (Optional — uses sample data)    │
│ Output: data/raw/*.csv                                      │
└────────────────────────────┬────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ MODULE 2: Preprocessing & Cleaning (REQUIRED)              │
│ • Timestamp parsing, missing value handling                │
│ • Date/time feature extraction (hour, day, week)           │
│ • Anomaly flagging, crowd ratio calculation                │
│ Output: data/cleaned/*.csv                                  │
└────────────────────────────┬────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ MODULE 3: Analytics & Aggregation (REQUIRED)               │
│ • Peak hour identification, daily/weekly trends             │
│ • Building/location utilization analysis                    │
│ Output: outputs/*.csv (peak_hours, daily_trends, etc.)      │
└────────────────────────────┬────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ MODULE 4: ML Models (Optional)                             │
│ • Predictive electricity/mess forecasting                   │
│ Output: models/*.pkl, outputs/predicted_*.csv               │
└────────────────────────────┬────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ MODULE 5: Recommendations (REQUIRED for Page 6)             │
│ • Smart recommendations with priority & ROI                │
│ Output: outputs/recommendations.csv                         │
└────────────────────────────┬────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ MODULE 6: Dashboard Preparation (REQUIRED)                 │
│ • Fact/dimension table generation                           │
│ • Calculated columns for BI tools                          │
│ Output: outputs/dashboard/*.csv (10 files)                  │
└────────────────────────────┬────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ LOCAL WEBSITE DASHBOARD                                     │
│ • 6 interactive pages with 30+ visuals                      │
│ • Dynamic cross-filtering & drill-down                      │
│ Output: local Flask web app at http://127.0.0.1:5000        │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start (5 Minutes)

### Step 1: Run Data Pipeline
```bash
# Prerequisites: Python 3.8+, pandas, numpy, scikit-learn (optional)
pip install -r requirements.txt

# Run ALL modules in sequence (recommended)
python module2_preprocessing.py
python module3_analytics.py
python module5_recommendations.py
python module6_dashboard_prep.py
```

### Step 2: Launch the Local Website
1. Run the dashboard app:
```bash
python app.py
```
2. Open **http://127.0.0.1:5000** in your browser
3. Refresh the page after rerunning the pipeline
4. Review energy, WiFi, mess, attendance, and recommendation insights

### Step 3: Explore and Share
1. Use the website to interact with the dashboard
2. Re-run the pipeline when new data arrives
3. Refresh the page to update the charts
4. Share the local URL with stakeholders on the same network

---

## File Structure

```
Campus_Intelligence_System/
├── README.md                          ← You are here
├── DASHBOARD_GUIDE.md                 ← Complete BI setup guide
├── QUICK_REFERENCE.md                 ← Printable reference card
├── requirements.txt                   ← Python dependencies
│
├── module1_data_generation.py          (Optional — creates raw data)
├── module2_preprocessing.py            (REQUIRED)
├── module3_analytics.py                (REQUIRED)
├── module4_ml_models.py                (Optional — ML predictions)
├── module5_recommendations.py          (REQUIRED)
├── module6_dashboard_prep.py           (REQUIRED — THIS IS KEY)
│
├── data/
│   ├── raw/                           (Sample data if using module1)
│   │   ├── attendance.csv
│   │   ├── electricity.csv
│   │   ├── mess_entry.csv
│   │   └── wifi_usage.csv
│   └── cleaned/                       (Module 2 output — clean data)
│       ├── attendance_clean.csv
│       ├── electricity_clean.csv
│       ├── mess_clean.csv
│       └── wifi_clean.csv
│
├── models/                            (Module 4 output — ML models)
│   ├── electricity_predictor.pkl
│   ├── mess_predictor.pkl
│   └── scaler.pkl
│
├── outputs/                           (Intermediate & final outputs)
│   ├── peak_hours.csv                 (Module 3)
│   ├── daily_trends.csv               (Module 3)
│   ├── weekly_trends.csv              (Module 3)
│   ├── electricity_utilization.csv    (Module 3)
│   ├── wifi_utilization.csv           (Module 3)
│   ├── detected_anomalies.csv         (Module 3)
│   ├── mess_peak_hours.csv            (Module 3)
│   ├── recommendations.csv            (Module 5)
│   ├── recommendations.txt            (Module 5 — human readable)
│   ├── predicted_electricity.csv      (Module 4 — optional)
│   ├── predicted_mess.csv             (Module 4 — optional)
│   │
│   └── dashboard/                     (Module 6 output — READY FOR BI)
│       ├── fact_electricity.csv       ✓ 4,455 rows
│       ├── fact_wifi.csv              ✓ 4,458 rows
│       ├── fact_mess.csv              ✓ 1,302 rows
│       ├── fact_attendance.csv        ✓ 16,745 rows
│       ├── fact_peak_hours.csv        ✓ 24 rows
│       ├── fact_daily_trends.csv      ✓ 31 rows
│       ├── fact_weekly_trends.csv     ✓ 5 rows
│       ├── fact_elec_utilization.csv  ✓ 6 rows
│       ├── fact_wifi_utilization.csv  ✓ 6 rows
│       └── dim_recommendations.csv    ✓ 27 rows
```

---

## Module Details

### Module 2: Data Preprocessing & Cleaning
**Purpose:** Transform raw data into analysis-ready format  
**Input:** `data/raw/*.csv` (sample data)  
**Output:** `data/cleaned/*.csv`  
**Key Operations:**
- Timestamp parsing & validation
- Missing value handling (forward fill, interpolation)
- Feature extraction (hour, day_of_week, week, month, is_weekend)
- Outlier flagging via IQR method
- Crowd ratio calculation (mess)
- Data quality validation

**Run:**
```bash
python module2_preprocessing.py
```

### Module 3: Analytics & Aggregation
**Purpose:** Calculate metrics & identify patterns  
**Input:** `data/cleaned/*.csv`  
**Output:** `outputs/*.csv` (peak_hours, trends, etc.)  
**Key Calculations:**
- Peak hour identification (top 25% users/energy)
- Daily & weekly aggregations
- Building/location utilization metrics
- Anomaly summary statistics

**Run:**
```bash
python module3_analytics.py
```

### Module 4: ML Models (Optional)
**Purpose:** Predict future resource usage  
**Input:** `data/cleaned/*.csv`  
**Output:** `models/*.pkl`, `outputs/predicted_*.csv`  
**Models:**
- ARIMA + Linear Regression (Electricity)
- Seasonal Decomposition (Mess)

**Run:**
```bash
python module4_ml_models.py
```

### Module 5: Recommendations
**Purpose:** Generate smart, actionable recommendations  
**Input:** `outputs/*.csv`, `data/cleaned/*.csv`  
**Output:** `outputs/recommendations.csv`  
**Recommendation Categories:**
- Energy Saving (High ROI)
- Mess Timing (Medium ROI)
- Class Scheduling (Low ROI)
- WiFi Optimization (Medium ROI)

**Run:**
```bash
python module5_recommendations.py
```

### Module 6: Dashboard Preparation ⭐ **THIS IS THE KEY**
**Purpose:** Generate dashboard-ready tables  
**Input:** `data/cleaned/*.csv`, `outputs/*.csv`  
**Output:** `outputs/dashboard/*.csv` (10 files)  
**Key Features:**
- Automatic calculated columns (hour_label, day_name, peak_indicator, etc.)
- Dimension table with auto-increment IDs
- Estimated savings extraction
- FutureWarnings eliminated
- Comprehensive error handling

**Run:**
```bash
python module6_dashboard_prep.py
```

**Expected Output:**
```
======================================================================
  ✓ SUCCESS: All dashboard CSVs saved to outputs/dashboard/

  ✓ fact_electricity: 4455 rows
  ✓ fact_wifi: 4458 rows
  ✓ fact_mess: 1302 rows
  ✓ fact_attendance: 16745 rows
  ✓ fact_peak_hours: 24 rows
  ✓ fact_weekly_trends: 5 rows
  ✓ dim_recommendations: 27 rows
  ✓ fact_daily_trends: 31 rows
  ✓ fact_elec_utilization: 6 rows
  ✓ fact_wifi_utilization: 6 rows
======================================================================
```

---

## Dashboard Overview

### 6 Interactive Pages

#### 📊 PAGE 1: Overview
- **Purpose:** Executive summary of campus utilization
- **Visuals:** 4 KPI cards + daily electricity trend
- **Slicers:** Date range
- **KPIs:** Avg electricity, peak mess hour, max WiFi users, avg attendance

#### 🏗️ PAGE 2: Resource Utilization
- **Purpose:** Building & location-level resource consumption
- **Visuals:** 2 bar charts (by building & location) + energy pie chart
- **Slicers:** Building, Location
- **Metrics:** Total electricity, WiFi users, energy distribution

#### ⏰ PAGE 3: Peak Hours Analysis
- **Purpose:** Identify capacity bottlenecks & peak periods
- **Visuals:** Heatmap (WiFi hour×day) + 2 line charts (electricity, WiFi)
- **Slicers:** Hour, Week type
- **Metrics:** Average users/units per hour, peak indicators

#### 📈 PAGE 4: Predictive Insights
- **Purpose:** Trend analysis & forecasting (if ML models available)
- **Visuals:** Multi-line weekly trends + area chart (electricity)
- **Slicers:** Week range
- **Metrics:** Weekly WiFi, mess entries, attendance, electricity
- **Note:** Shows "Actual vs Predicted" if module4 was executed

#### 🚨 PAGE 5: Anomaly Detection
- **Purpose:** Flag unusual electricity consumption patterns
- **Visuals:** Scatter plot + anomaly records table + count card
- **Slicers:** Anomaly flag, Date range
- **Metrics:** Anomaly events, affected buildings, consumption spikes

#### 💡 PAGE 6: Recommendations
- **Purpose:** Display AI-generated optimization recommendations
- **Visuals:** Dynamic table with priority-based filtering
- **Slicers:** Category, Priority
- **Metrics:** 27+ recommendations with ROI, priority ranking, categories

---

## Power BI Implementation Quick Reference

### Create Relationships (Model View)

```
drag:                           to:
─────────────────────────────────────────────────────
fact_daily_trends[date]     → fact_electricity[date]
fact_daily_trends[date]     → fact_wifi[date]
fact_daily_trends[date]     → fact_mess[date]
fact_daily_trends[date]     → fact_attendance[date]
fact_peak_hours[hour]       → fact_electricity[hour]
fact_peak_hours[hour]       → fact_wifi[hour]
fact_weekly_trends[week]    → fact_daily_trends[week]
```

### Paste Essential Measures (New Measure)

```dax
Avg Electricity (kWh) = AVERAGE(fact_electricity[units_consumed])

Max WiFi Users = MAX(fact_wifi[number_of_users])

Energy Share % = DIVIDE(
    SUM(fact_electricity[units_consumed]),
    CALCULATE(SUM(fact_electricity[units_consumed]), ALL(fact_electricity))
) * 100

Anomaly Count = CALCULATE(
    COUNT(fact_electricity[is_anomaly]),
    fact_electricity[is_anomaly] = 1
)
```

**See DASHBOARD_GUIDE.md for complete DAX formulas (15+ measures)**

### Global Slicers (Enable Cross-Page)

View → Sync Slicers → check all pages for:
- Date Range → `fact_daily_trends[date]`
- Building → `fact_electricity[building]`
- Location → `fact_wifi[location]`
- Week Type → `fact_electricity[week_type]`
- Hour → `fact_peak_hours[hour_label]`

---

## Tableau Implementation Quick Reference

### Create Relationships (Data Source Tab)

Drag `fact_daily_trends` to canvas, then add:
- `fact_electricity` → relate on [date]=[date]
- `fact_wifi` → relate on [date]=[date]
- `fact_mess` → relate on [date]=[date]
- `fact_attendance` → relate on [date]=[date]
- `fact_peak_hours` → relate on [hour]=[hour]

### Create Calculated Fields

**Hour Label**
```
STR(INT([Hour])) + ":00–" + STR(INT([Hour])+1) + ":00"
```

**Peak Indicator**
```
IF [Units Consumed] > 20 THEN "High"
ELSEIF [Units Consumed] > 10 THEN "Medium"
ELSE "Low" END
```

**Attendance Rate %**
```
AVG([Is Present]) * 100
```

**Energy Share %**
```
SUM([Units Consumed]) / TOTAL(SUM([Units Consumed])) * 100
```

**See DASHBOARD_GUIDE.md for complete calculated field formulas (8+ fields)**

---

## Color Palette (Use Consistently)

### Status Colors
- 🔴 **High/Alert/Peak:** #E74C3C (Red)
- 🟠 **Medium/Warning:** #E67E22 (Orange)
- 🟢 **Low/Safe/Normal:** #2ECC71 (Green)
- 🔵 **Info/WiFi:** #3498DB (Blue)

### Building Colors (Fixed)
- **Academic Block A:** #3498DB
- **Academic Block B:** #2980B9
- **Hostel Block 1:** #E74C3C
- **Hostel Block 2:** #C0392B
- **Library:** #9B59B6
- **Sports Complex:** #1ABC9C

### Priority Colors (Recommendations Table)
- **High:** bg #FADBD8 | text #E74C3C
- **Medium:** bg #FDEBD0 | text #E67E22
- **Low:** bg #D5F5E3 | text #27AE60

---

## Data Dictionary

### Common Fields Across Tables

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `timestamp` | DateTime | 2024-03-01 onwards | Full datetime of event |
| `date` | Date | 2024-03-01 onwards | Date only (no time) |
| `hour` | Integer | 0-23 | Hour of day (24-hour format) |
| `day_of_week` | Integer | 0-6 | Monday (0) to Sunday (6) |
| `week` | Integer | 1-52 | ISO week number of year |
| `is_weekend` | Integer | 0 or 1 | 0=Weekday, 1=Weekend |
| `is_anomaly` | Integer | 0 or 1 | 0=Normal, 1=Outlier detected |
| `building` | Text | "Academic Block A", etc. | Building name |
| `location` | Text | "Academic Zone", etc. | WiFi location name |
| `meal_type` | Text | "Breakfast", "Lunch", etc. | Meal service type |

### Calculated Columns (Added by Module 6)

| Column | Calculation | Example |
|--------|-------------|---------|
| `hour_label` | str(hour) + ":00–" + str(hour+1) + ":00" | "09:00–10:00" |
| `day_name` | Map day_of_week to name | "Friday" |
| `week_type` | "Weekend" if is_weekend else "Weekday" | "Weekday" |
| `week_label` | "Week " + str(week) | "Week 9" |
| `month_name` | Format date as "Mon YYYY" | "Mar 2024" |
| `peak_indicator` | "High" if >20, "Medium" if 10-20, "Low" | "High" |
| `load_level` | "High" if >150, "Medium" if 50-150, "Low" | "Medium" |
| `crowd_level` | "High" if >0.6, "Medium" if 0.3-0.6, "Low" | "High" |
| `time_slot_label` | meal_type + " " + hour_label | "Breakfast 08:00" |
| `priority_rank` | 1 if High, 2 if Medium, 3 if Low | 1 |

---

## Troubleshooting & FAQs

### Q: I get "File not found" when running module6
**A:** Ensure modules 2, 3, and 5 were executed first in order.
```bash
python module2_preprocessing.py  # Creates cleaned data
python module3_analytics.py      # Creates peak_hours, trends
python module5_recommendations.py # Creates recommendations
python module6_dashboard_prep.py  # Creates dashboard CSVs
```

### Q: Module 6 runs but outputs are empty or missing
**A:** Check that all 10 CSV files exist in `outputs/dashboard/`:
```bash
dir outputs\dashboard\  # Windows
ls outputs/dashboard/   # Mac/Linux
```
Should show 10 files. If <10, check error messages in module output.

### Q: Power BI relationships don't show up
**A:** Verify:
1. All 10 CSVs imported as tables (not queries)
2. Date columns are `Date` type, not `Text`
3. Hour columns are `Whole Number`, not `Text`
4. Column names match exactly

### Q: DAX formula shows "Table of ..." or #ERROR
**A:**
1. Copy formula exactly (watch indentation & brackets)
2. Verify table/column names exist
3. Use SINGLE quotes for column names with spaces
4. Test with simple measures first

### Q: Slicers don't filter charts
**A:**
1. Verify relationships exist in Model view
2. Check cross-filter direction is "Both"
3. Enable "Sync Slicers" across pages
4. Test with simplest slicer first

### Q: Dashboard is slow/unresponsive
**A:**
1. Filter to smaller date range
2. Aggregate data weekly instead of daily
3. Use DirectQuery for large datasets
4. Reduce number of simultaneous visuals

### Q: Anomaly page shows no data
**A:**
1. Verify `is_anomaly` field exists in electricity_clean.csv
2. Check that some rows have `is_anomaly = 1`
3. Apply filter: `is_anomaly = 1` (not `= 0`)
4. Verify date range includes anomaly records

---

## Next Steps

1. ✅ **Run Module 6** → Generate dashboard CSVs
2. ✅ **Choose BI Tool** → Power BI (recommended) or Tableau
3. ✅ **Import Data** → Import all 10 CSVs from `outputs/dashboard/`
4. ✅ **Create Relationships** → Follow relationship diagram
5. ✅ **Add Measures** → Paste DAX formulas (Power BI) or calculated fields (Tableau)
6. ✅ **Build Pages** → Follow page-by-page guide in DASHBOARD_GUIDE.md
7. ✅ **Apply Theme** → Use color palette & formatting specs
8. ✅ **Enable Slicers** → Cross-page filtering
9. ✅ **Publish** → Deploy to Power BI Service / Tableau Server
10. ✅ **Share** → Distribute to stakeholders

---

## Documentation Files

| File | Purpose | Audience |
|------|---------|----------|
| **README.md** | System overview & quick start | Everyone |
| **DASHBOARD_GUIDE.md** | Complete BI implementation guide | BI Tool Builders |
| **QUICK_REFERENCE.md** | Printable color/formula reference | Developers |
| **module6_dashboard_prep.py** | Data preparation script | Data Engineers |

---

## Support Resources

**Documentation:**
- DASHBOARD_GUIDE.md — Full step-by-step setup
- QUICK_REFERENCE.md — Printable reference card
- Code comments in all module files

**Troubleshooting:**
1. Check error messages in terminal output
2. Verify file paths and data types
3. Test formulas individually
4. Check DASHBOARD_GUIDE.md FAQ section

**Performance Optimization:**
- Use date range filters to reduce data volume
- Pre-aggregate data for large datasets
- Enable query folding in Power BI
- Use DirectQuery for real-time data

---

## License & Attribution

This Smart Campus Intelligence System is developed for educational and enterprise use.

**Key Technologies:**
- Python 3.8+ (pandas, numpy, scikit-learn)
- Power BI Desktop / Tableau Desktop
- SQL-based data warehousing (optional)

**Data Privacy:**
- All student/personal data should be anonymized
- Comply with GDPR, FERPA, and local regulations
- Secure dashboard access with authentication

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| **1.0** | Apr 2026 | Initial release with 6 modules, 10 dashboard tables, 6 BI pages |

---

## Contact & Feedback

For questions, bugs, or feature requests:
1. Check DASHBOARD_GUIDE.md Troubleshooting section
2. Review QUICK_REFERENCE.md for common issues
3. Inspect error messages in terminal output
4. Validate data in `outputs/dashboard/` CSVs

---

**Ready to build your dashboard?** Start with:
```bash
python module6_dashboard_prep.py
```

Then open DASHBOARD_GUIDE.md for complete Power BI/Tableau setup instructions!

---

*Smart Campus Intelligence System v1.0*  
*April 2026*  
*✅ Production Ready*
