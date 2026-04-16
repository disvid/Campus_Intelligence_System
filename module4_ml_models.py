"""
MODULE 4: Machine Learning Models
Smart Campus Intelligence System

1. Mess Crowd Prediction — Gradient Boosted Regression
2. Electricity Forecasting — Random Forest Regression
3. Anomaly Detection — Isolation Forest (electricity/WiFi)

Each model: train/test split, evaluation (MAE, RMSE), save/load.
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import (GradientBoostingRegressor,
                              RandomForestRegressor,
                              IsolationForest)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

os.makedirs('models', exist_ok=True)


# ─── Utility ──────────────────────────────────────────────────────────────────
def rmse(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))

def save_model(obj, path):
    with open(path, 'wb') as f:
        pickle.dump(obj, f)
    print(f"  Model saved → {path}")

def load_model(path):
    with open(path, 'rb') as f:
        return pickle.load(f)


# ════════════════════════════════════════════════════════════════════════════════
# MODEL 1: MESS CROWD PREDICTION
# ════════════════════════════════════════════════════════════════════════════════
def train_mess_model():
    print("\n[1] Training Mess Crowd Prediction model...")

    df = pd.read_csv('data/cleaned/mess_clean.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Feature engineering
    df['hour']        = df['timestamp'].dt.hour
    df['minute']      = df['timestamp'].dt.minute
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_weekend']  = (df['day_of_week'] >= 5).astype(int)
    df['day_of_month'] = df['timestamp'].dt.day

    # Lag features: previous slot's crowd
    df = df.sort_values('timestamp').reset_index(drop=True)
    df['prev_students'] = df['number_of_students'].shift(1).fillna(
        df['number_of_students'].mean()
    )
    df['rolling_mean_3'] = (
        df['number_of_students'].rolling(window=3, min_periods=1).mean().shift(1)
        .fillna(df['number_of_students'].mean())
    )

    FEATURES = [
        'hour', 'minute', 'day_of_week', 'is_weekend',
        'meal_slot', 'day_of_month', 'prev_students', 'rolling_mean_3'
    ]
    TARGET = 'number_of_students'

    df_model = df[FEATURES + [TARGET]].dropna()
    X = df_model[FEATURES].values
    y = df_model[TARGET].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, shuffle=False
    )

    # Scale
    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)

    # Model
    model = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.08,
        max_depth=4,
        subsample=0.85,
        random_state=42
    )
    model.fit(X_train_sc, y_train)

    # Evaluate
    y_pred = model.predict(X_test_sc)
    y_pred = np.clip(y_pred, 0, None)

    mae  = mean_absolute_error(y_test, y_pred)
    rmse_val = rmse(y_test, y_pred)
    mape = np.mean(np.abs((y_test - y_pred) / (y_test + 1e-6))) * 100

    print(f"  Train size : {len(X_train):,}")
    print(f"  Test  size : {len(X_test):,}")
    print(f"  MAE        : {mae:.2f} students")
    print(f"  RMSE       : {rmse_val:.2f} students")
    print(f"  MAPE       : {mape:.1f}%")

    # Feature importance
    fi = pd.DataFrame({
        'feature':   FEATURES,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    print("\n  Feature Importances:")
    print(fi.to_string(index=False))

    # Sample predictions
    sample = pd.DataFrame(X_test[:5], columns=FEATURES)
    sample['actual']    = y_test[:5]
    sample['predicted'] = np.round(y_pred[:5], 1)
    print("\n  Sample predictions (first 5 test rows):")
    print(sample[['hour', 'meal_slot', 'is_weekend',
                  'actual', 'predicted']].to_string(index=False))

    save_model({'model': model, 'scaler': scaler, 'features': FEATURES},
               'models/mess_crowd_model.pkl')
    return model, scaler


# ════════════════════════════════════════════════════════════════════════════════
# MODEL 2: ELECTRICITY FORECASTING
# ════════════════════════════════════════════════════════════════════════════════
def train_electricity_model():
    print("\n[2] Training Electricity Forecasting model...")

    df = pd.read_csv('data/cleaned/electricity_clean.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Remove anomalous rows from training set
    df = df[df['is_anomaly'] == 0].copy()

    # Label encode building
    df['building_code'] = df['building'].astype('category').cat.codes

    # Lag & rolling features
    df = df.sort_values(['building', 'timestamp']).reset_index(drop=True)
    df['lag_1h']    = df.groupby('building')['units_consumed'].shift(1)
    df['lag_24h']   = df.groupby('building')['units_consumed'].shift(24)
    df['roll_6h']   = (df.groupby('building')['units_consumed']
                       .transform(lambda x: x.rolling(6,  min_periods=1).mean().shift(1)))
    df['roll_24h']  = (df.groupby('building')['units_consumed']
                       .transform(lambda x: x.rolling(24, min_periods=1).mean().shift(1)))

    df.dropna(inplace=True)

    FEATURES = [
        'hour', 'day_of_week', 'is_weekend', 'building_code',
        'lag_1h', 'lag_24h', 'roll_6h', 'roll_24h'
    ]
    TARGET = 'units_consumed'

    X = df[FEATURES].values
    y = df[TARGET].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, shuffle=False
    )

    model = RandomForestRegressor(
        n_estimators=150,
        max_depth=10,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_pred = np.clip(y_pred, 0, None)

    mae_val  = mean_absolute_error(y_test, y_pred)
    rmse_val = rmse(y_test, y_pred)
    r2       = model.score(X_test, y_test)

    print(f"  Train size : {len(X_train):,}")
    print(f"  Test  size : {len(X_test):,}")
    print(f"  MAE        : {mae_val:.3f} units")
    print(f"  RMSE       : {rmse_val:.3f} units")
    print(f"  R²         : {r2:.4f}")

    fi = pd.DataFrame({
        'feature':    FEATURES,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    print("\n  Feature Importances:")
    print(fi.to_string(index=False))

    # Save building code mapping for inference
    building_map = dict(enumerate(
        df['building'].astype('category').cat.categories
    ))

    save_model({'model': model, 'features': FEATURES,
                'building_map': building_map},
               'models/electricity_model.pkl')
    return model


# ════════════════════════════════════════════════════════════════════════════════
# MODEL 3: ANOMALY DETECTION
# ════════════════════════════════════════════════════════════════════════════════
def train_anomaly_detector():
    print("\n[3] Training Anomaly Detection model (Isolation Forest)...")

    # Combine electricity + WiFi features for anomaly detection
    elec_df = pd.read_csv('data/cleaned/electricity_clean.csv')
    wifi_df = pd.read_csv('data/cleaned/wifi_clean.csv')

    elec_df['timestamp'] = pd.to_datetime(elec_df['timestamp'])
    wifi_df['timestamp'] = pd.to_datetime(wifi_df['timestamp'])

    # Aggregate to hourly campus-level
    elec_hourly = (elec_df.groupby(elec_df['timestamp'].dt.floor('H'))
                   ['units_consumed'].sum()
                   .reset_index()
                   .rename(columns={'timestamp': 'ts',
                                    'units_consumed': 'total_units'}))

    wifi_hourly = (wifi_df.groupby(wifi_df['timestamp'].dt.floor('H'))
                   ['number_of_users'].sum()
                   .reset_index()
                   .rename(columns={'timestamp': 'ts',
                                    'number_of_users': 'total_users'}))

    merged = elec_hourly.merge(wifi_hourly, on='ts', how='inner')
    merged['hour']        = merged['ts'].dt.hour
    merged['day_of_week'] = merged['ts'].dt.dayofweek

    FEATURES = ['total_units', 'total_users', 'hour', 'day_of_week']
    X = merged[FEATURES].dropna().values

    # Isolation Forest: contamination ~5% (expected anomaly rate)
    iso_forest = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42,
        n_jobs=-1
    )
    iso_forest.fit(X)

    # Evaluate on the training set itself (unsupervised)
    preds  = iso_forest.predict(X)            # -1 = anomaly, 1 = normal
    scores = iso_forest.score_samples(X)      # lower = more anomalous
    anomaly_count = (preds == -1).sum()
    print(f"  Total hourly records : {len(X):,}")
    print(f"  Detected anomalies   : {anomaly_count} ({anomaly_count/len(X)*100:.1f}%)")
    print(f"  Avg anomaly score    : {scores[preds == -1].mean():.4f}")
    print(f"  Avg normal score     : {scores[preds == 1].mean():.4f}")

    # Sample anomalies
    anom_df = merged.iloc[:len(X)].copy()
    anom_df['anomaly_pred']  = preds
    anom_df['anomaly_score'] = scores
    anomalies = anom_df[anom_df['anomaly_pred'] == -1].nsmallest(5, 'anomaly_score')
    print("\n  Top 5 most anomalous records:")
    print(anomalies[['ts', 'total_units', 'total_users',
                      'anomaly_score']].to_string(index=False))

    anomalies.to_csv('outputs/detected_anomalies.csv', index=False)

    save_model({'model': iso_forest, 'features': FEATURES},
               'models/anomaly_model.pkl')
    return iso_forest


# ════════════════════════════════════════════════════════════════════════════════
# INFERENCE HELPERS
# ════════════════════════════════════════════════════════════════════════════════
def predict_mess_crowd(hour, day_of_week, meal_slot, is_weekend,
                       prev_students=None, model_path='models/mess_crowd_model.pkl'):
    """
    Predict expected mess crowd for given time/day.
    meal_slot: 0=Breakfast, 1=Lunch, 2=Snacks, 3=Dinner
    """
    artifact = load_model(model_path)
    model    = artifact['model']
    scaler   = artifact['scaler']
    features = artifact['features']

    # Use average prev_students if not provided
    if prev_students is None:
        prev_students = 300

    X = np.array([[
        hour, 0, day_of_week, is_weekend,
        meal_slot, 15, prev_students, prev_students
    ]])
    X_sc = scaler.transform(X)
    pred = model.predict(X_sc)[0]
    return max(0, round(pred, 1))


def predict_electricity(building, hour, day_of_week, is_weekend,
                        lag_1h, lag_24h, roll_6h, roll_24h,
                        model_path='models/electricity_model.pkl'):
    """Predict electricity consumption for a building at a given hour."""
    artifact     = load_model(model_path)
    model        = artifact['model']
    building_map = artifact['building_map']

    # Reverse lookup building code
    inv_map = {v: k for k, v in building_map.items()}
    bldg_code = inv_map.get(building, 0)

    X = np.array([[
        hour, day_of_week, is_weekend, bldg_code,
        lag_1h, lag_24h, roll_6h, roll_24h
    ]])
    pred = model.predict(X)[0]
    return max(0.0, round(pred, 3))


# ════════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 55)
    print("  Smart Campus — Module 4: ML Models")
    print("=" * 55)

    mess_model = train_mess_model()
    elec_model = train_electricity_model()
    anom_model = train_anomaly_detector()

    print("\n" + "─" * 55)
    print("  Quick Inference Tests")
    print("─" * 55)

    # Test mess prediction: Lunch on Monday (day=0)
    pred_crowd = predict_mess_crowd(
        hour=13, day_of_week=0, meal_slot=1, is_weekend=0,
        prev_students=450
    )
    print(f"\n  Predicted lunch crowd (Mon 1PM) : {pred_crowd} students")

    # Test electricity: Academic Block A on Monday 10 AM
    pred_units = predict_electricity(
        building='Academic Block A', hour=10, day_of_week=0, is_weekend=0,
        lag_1h=42.0, lag_24h=40.5, roll_6h=38.0, roll_24h=37.5
    )
    print(f"  Predicted electricity (AcadA Mon 10AM) : {pred_units} units")

    print("\nAll models saved in models/")