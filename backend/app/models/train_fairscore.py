"""
Train XGBoost model for FairScore prediction.

This script:
1. Loads synthetic_fairscore_dataset.csv
2. Trains an XGBoost regressor
3. Saves model + feature scaler to disk
"""

import os
import pickle
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

# Paths
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
DATASET_PATH = DATA_DIR / "synthetic_fairscore_dataset.csv"
MODEL_DIR = Path(__file__).parent
MODEL_PATH = MODEL_DIR / "fairscore_model.pkl"
SCALER_PATH = MODEL_DIR / "fairscore_scaler.pkl"

FEATURE_COLS = [
    "avg_inflow",
    "avg_outflow",
    "savings_rate",
    "volatility",
    "academic_score",
    "part_time_income",
    "emi_count",
]
TARGET_COL = "label_score"


def train_model():
    """Train XGBoost model and save artifacts."""
    print(f"Loading dataset from {DATASET_PATH}")
    
    if not DATASET_PATH.exists():
        print(f"ERROR: Dataset not found at {DATASET_PATH}")
        print("Please run: python data/generate_fairscore_dataset.py")
        return
    
    df = pd.read_csv(DATASET_PATH)
    print(f"Loaded {len(df)} rows")
    
    X = df[FEATURE_COLS]
    y = df[TARGET_COL]
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train XGBoost
    print("Training XGBoost model...")
    model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
    )
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    train_score = model.score(X_train_scaled, y_train)
    test_score = model.score(X_test_scaled, y_test)
    print(f"Train R²: {train_score:.3f}")
    print(f"Test R²: {test_score:.3f}")
    
    # Save model and scaler
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print(f"Model saved to {MODEL_PATH}")
    
    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)
    print(f"Scaler saved to {SCALER_PATH}")
    
    print("Training complete!")


if __name__ == "__main__":
    train_model()
