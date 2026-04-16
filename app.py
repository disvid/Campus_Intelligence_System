from pathlib import Path
import json

from flask import Flask, render_template, abort
import pandas as pd

app = Flask(__name__)

DATA_DIR = Path('outputs/dashboard')
REQUIRED_FILES = [
    'fact_electricity.csv',
    'fact_wifi.csv',
    'fact_mess.csv',
    'fact_attendance.csv',
    'fact_peak_hours.csv',
    'fact_daily_trends.csv',
    'fact_weekly_trends.csv',
    'dim_recommendations.csv',
]


def load_csv(filename, parse_dates=None):
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f'Missing required dashboard file: {path}')
    return pd.read_csv(path, parse_dates=parse_dates)


def load_dashboard_data():
    data = {
        'electricity': load_csv('fact_electricity.csv', parse_dates=['timestamp', 'date']),
        'wifi': load_csv('fact_wifi.csv', parse_dates=['timestamp', 'date']),
        'mess': load_csv('fact_mess.csv', parse_dates=['timestamp', 'date']),
        'attendance': load_csv('fact_attendance.csv', parse_dates=['date']),
        'peak_hours': load_csv('fact_peak_hours.csv'),
        'daily_trends': load_csv('fact_daily_trends.csv', parse_dates=['date']),
        'weekly_trends': load_csv('fact_weekly_trends.csv'),
        'recommendations': enhance_recommendations(load_csv('dim_recommendations.csv')),
    }
    return data


def enhance_recommendations(df):
    """Enhance recommendations data with detailed fields for dashboard display"""
    if df.empty:
        return df

    # Add missing columns with enhanced data
    if 'subcategory' not in df.columns:
        df['subcategory'] = df['category'].map({
            'Mess Timing': 'Mess Optimization',
            'Energy Saving': 'Building Automation',
            'Class Scheduling': 'Academic Planning',
            'Infrastructure / WiFi Capacity': 'Network Infrastructure',
            'Resource Allocation': 'Facility Utilization'
        }).fillna(df['category'])

    if 'ease_of_implementation' not in df.columns:
        df['ease_of_implementation'] = df.apply(lambda row: get_implementation_ease(row), axis=1)

    if 'timeframe' not in df.columns:
        df['timeframe'] = df['priority'].map({
            'High': 'Immediate',
            'Medium': '1-3 months',
            'Low': 'Semester planning'
        })

    if 'problem_detected' not in df.columns:
        df['problem_detected'] = df['category'].map({
            'Mess Timing': 'Peak crowding at meal times',
            'Energy Saving': 'Wasted electricity during off-hours',
            'Class Scheduling': 'Suboptimal scheduling patterns',
            'Infrastructure / WiFi Capacity': 'WiFi overload at peak locations',
            'Resource Allocation': 'Underutilized facilities'
        }).fillna('Operational inefficiency detected')

    if 'data_insight' not in df.columns:
        df['data_insight'] = df.apply(lambda row: extract_insight(row), axis=1)

    if 'suggested_action' not in df.columns:
        df['suggested_action'] = df.apply(lambda row: extract_action(row), axis=1)

    if 'expected_impact' not in df.columns:
        df['expected_impact'] = df['category'].map({
            'Mess Timing': 'Reduce wait times and improve student satisfaction',
            'Energy Saving': 'Save electricity costs and reduce carbon footprint',
            'Class Scheduling': 'Better resource utilization and improved attendance',
            'Infrastructure / WiFi Capacity': 'Improved connectivity and user experience',
            'Resource Allocation': 'Optimized facility usage and cost savings'
        }).fillna('Enhanced operational efficiency')

    if 'icon' not in df.columns:
        df['icon'] = df['category'].map({
            'Mess Timing': 'fas fa-utensils',
            'Energy Saving': 'fas fa-bolt',
            'Class Scheduling': 'fas fa-calendar-alt',
            'Infrastructure / WiFi Capacity': 'fas fa-wifi',
            'Resource Allocation': 'fas fa-building'
        }).fillna('fas fa-lightbulb')

    if 'color' not in df.columns:
        df['color'] = df['category'].map({
            'Mess Timing': 'success',
            'Energy Saving': 'warning',
            'Class Scheduling': 'info',
            'Infrastructure / WiFi Capacity': 'danger',
            'Resource Allocation': 'secondary'
        }).fillna('primary')

    return df


def get_implementation_ease(row):
    """Determine implementation ease based on recommendation content"""
    rec_text = str(row['recommendation']).lower()
    if 'self-study' in rec_text or 'reallocate' in rec_text:
        return 'Easy'
    elif 'automated' in rec_text or 'add access points' in rec_text:
        return 'Hard'
    else:
        return 'Medium'


def extract_insight(row):
    """Extract data insight from recommendation"""
    rec = str(row['recommendation'])
    if 'avg' in rec and 'vs' in rec:
        # Extract numbers for mess timing
        import re
        numbers = re.findall(r'(\d+)', rec)
        if len(numbers) >= 2:
            return f"Average {numbers[0]} students during recommended time vs {numbers[1]} during peak"
    elif 'units wasted' in rec:
        return "Significant electricity waste during low-occupancy hours"
    elif 'attendance' in rec:
        return "Low attendance rates on certain days"
    else:
        return "Data analysis indicates optimization opportunity"


def extract_action(row):
    """Extract suggested action"""
    rec = str(row['recommendation'])
    if 'Visit' in rec:
        return rec.split('—')[0].strip()
    elif 'Schedule' in rec:
        return "Adjust class scheduling patterns"
    elif 'Implement' in rec:
        return "Deploy automated energy management"
    elif 'Add access' in rec:
        return "Expand network infrastructure"
    elif 'Consider' in rec:
        return "Reallocate resources efficiently"
    else:
        return rec.split('—')[0].strip() if '—' in rec else rec


def safe_json(payload):
    # Keep the payload as native Python objects so Jinja can serialize it properly.
    return payload


def prepare_context():
    ds = load_dashboard_data()
    elec = ds['electricity']
    wifi = ds['wifi']
    mess = ds['mess']
    att = ds['attendance']
    peak = ds['peak_hours']
    daily = ds['daily_trends']
    recs = ds['recommendations']

    total_energy = float(elec['units_consumed'].sum())
    avg_wifi_users = float(wifi['number_of_users'].mean())
    total_attendance = int(len(att))
    present_rate = round(float(att['is_present'].mean() * 100), 1) if 'is_present' in att.columns else None
    anomaly_count = int(elec['is_anomaly'].sum()) if 'is_anomaly' in elec.columns else 0
    recommendation_count = len(recs)
    high_priority = int((recs['priority'] == 'High').sum()) if 'priority' in recs.columns else 0

    electricity_chart = {
        'x': daily['date'].dt.strftime('%Y-%m-%d').tolist(),
        'y': daily['total_units'].fillna(0).astype(float).tolist(),
        'name': 'Electricity Consumption',
    }

    wifi_location = (wifi.groupby('location')['number_of_users']
                     .sum()
                     .sort_values(ascending=False)
                     .reset_index())
    mess_meal = (mess.groupby('meal_type')['number_of_students']
                 .mean()
                 .sort_values(ascending=False)
                 .reset_index())
    attendance_day = (att.groupby('day_name')['is_present']
                      .mean()
                      .reset_index())
    attendance_day['attendance_pct'] = (attendance_day['is_present'] * 100).round(1)

    rec_categories = (recs.groupby('category').size()
                      .reset_index(name='count')
                      .sort_values('count', ascending=False))

    peak_by_hour = (peak.sort_values('hour')
                    .assign(hour=lambda df: df['hour'].astype(int)))

    rec_rows = recs.copy()
    if 'priority_rank' in rec_rows.columns:
        rec_rows.sort_values(['priority_rank', 'category'], inplace=True)
    else:
        rec_rows.sort_values(['category'], inplace=True)
    rec_rows = rec_rows.head(25)
    record_rows = rec_rows.to_dict(orient='records')

    return {
        'metrics': {
            'total_energy': round(total_energy, 1),
            'avg_wifi_users': round(avg_wifi_users, 1),
            'total_attendance': total_attendance,
            'present_rate': present_rate,
            'anomaly_count': anomaly_count,
            'recommendation_count': recommendation_count,
            'high_priority': high_priority,
        },
        'charts': {
            'electricity': safe_json(electricity_chart),
            'wifi_location': safe_json({
                'labels': wifi_location['location'].tolist(),
                'values': wifi_location['number_of_users'].astype(int).tolist(),
            }),
            'mess_meal': safe_json({
                'labels': mess_meal['meal_type'].tolist(),
                'values': mess_meal['number_of_students'].round(1).tolist(),
            }),
            'attendance': safe_json({
                'labels': attendance_day['day_name'].tolist(),
                'values': attendance_day['attendance_pct'].tolist(),
            }),
            'recommendations': safe_json({
                'labels': rec_categories['category'].tolist(),
                'values': rec_categories['count'].tolist(),
            }),
            'peak_hours': safe_json({
                'labels': peak_by_hour['hour'].astype(str).tolist(),
                'electricity': peak_by_hour['avg_units'].round(1).astype(float).tolist(),
                'wifi': peak_by_hour['avg_wifi_users'].round(1).astype(float).tolist(),
            }),
        },
        'tables': {
            'recommendations': record_rows,
        },
    }


@app.route('/')
def dashboard():
    try:
        ctx = prepare_context()
    except FileNotFoundError as exc:
        message = str(exc) + '. Please run module6_dashboard_prep.py first.'
        abort(500, message)

    return render_template('dashboard.html', **ctx)


@app.errorhandler(500)
def handle_error(error):
    message = getattr(error, 'description', str(error))
    return render_template('error.html', message=message), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
