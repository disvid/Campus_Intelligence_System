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
        'recommendations': load_csv('dim_recommendations.csv'),
    }
    return data


def safe_json(payload):
    return json.dumps(payload, default=str)


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
