# ============================================================
# OCEANEMBED STEP 32
# LIGHTWEIGHT DEPTH-AWARE NEURAL NETWORK
# ============================================================

import os
import sys
import joblib
import numpy as np
import pandas as pd

from pathlib import Path

from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ============================================================
# 1. FIND PROJECT ROOT AUTOMATICALLY
# ============================================================

CURRENT_FILE = Path(__file__).resolve()

# Current file:
# OceanEmbed/ml/train_step32_neural.py
#
# Therefore:
# CURRENT_FILE.parent       = ml
# CURRENT_FILE.parent.parent = OceanEmbed

PROJECT_ROOT = CURRENT_FILE.parent.parent

DATA_FILE = PROJECT_ROOT / "ml" / "data" / "real" / "multidate_real_training.csv"

MODEL_DIR = PROJECT_ROOT / "ml" / "models"
OUTPUT_DIR = PROJECT_ROOT / "data" / "real"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_FILE = MODEL_DIR / "oceanembed_step32_neural.pkl"

PREDICTIONS_FILE = OUTPUT_DIR / "step32_neural_predictions.csv"

DEPTH_ERROR_FILE = OUTPUT_DIR / "step32_neural_depth_error.csv"


# ============================================================
# 2. SETTINGS
# ============================================================

RANDOM_STATE = 42

MAX_TRAIN_SAMPLES = 150_000

HIDDEN_LAYERS = (64, 32)

MAX_ITER = 30


# ============================================================
# 3. PRINT PROJECT INFORMATION
# ============================================================

print("=" * 70)
print("OCEANEMBED STEP 32")
print("LIGHTWEIGHT DEPTH-AWARE NEURAL NETWORK")
print("=" * 70)

print()

print("Project root:")
print(PROJECT_ROOT)

print()

print("Dataset:")
print(DATA_FILE)

print()


# ============================================================
# 4. CHECK DATASET
# ============================================================

if not DATA_FILE.exists():

    print("ERROR: Dataset not found.")
    print()

    print("Expected file:")
    print(DATA_FILE)

    print()

    print("Please check whether this file exists:")
    print(
        PROJECT_ROOT
        / "data"
        / "real"
        / "multidate_real_training.csv"
    )

    print()

    print("You can check manually using:")
    print(
        f'Test-Path "{PROJECT_ROOT / "data" / "real" / "multidate_real_training.csv"}"'
    )

    sys.exit(1)


print("Dataset found successfully.")

print()


# ============================================================
# 5. LOAD DATA
# ============================================================

print("Loading dataset...")

df = pd.read_csv(DATA_FILE)

print("Dataset loaded.")

print()

print("Number of records:", len(df))

print()

print("Columns:")
print(df.columns.tolist())

print()


# ============================================================
# 6. CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "date",
    "latitude",
    "longitude",
    "depth",
    "sst",
    "sss",
    "ssh",
    "current_u",
    "current_v",
    "temperature"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    print("ERROR: Missing columns:")

    for column in missing_columns:
        print(" -", column)

    sys.exit(1)


# ============================================================
# 7. CLEAN DATA
# ============================================================

print("Cleaning data...")

df["date"] = pd.to_datetime(df["date"])

numeric_columns = [
    "latitude",
    "longitude",
    "depth",
    "sst",
    "sss",
    "ssh",
    "current_u",
    "current_v",
    "temperature"
]

for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

before = len(df)

df = df.dropna(
    subset=numeric_columns
).reset_index(drop=True)

after = len(df)

print("Removed rows:", before - after)

print("Remaining rows:", after)

print()


# ============================================================
# 8. TEMPORAL TRAIN / TEST SPLIT
# ============================================================

print("Creating temporal train/test split...")

# Training:
# January 2020 -> August 2020
#
# Testing:
# September 2020 -> October 2020

train_mask = df["date"] < pd.Timestamp("2020-09-01")

test_mask = df["date"] >= pd.Timestamp("2020-09-01")

train_df = df.loc[train_mask].copy()

test_df = df.loc[test_mask].copy()

print()

print("Training records:", len(train_df))

print("Testing records :", len(test_df))

print()

print("Training dates:")

print(
    train_df["date"]
    .dt.strftime("%Y-%m-%d")
    .unique()
)

print()

print("Testing dates:")

print(
    test_df["date"]
    .dt.strftime("%Y-%m-%d")
    .unique()
)

print()


# ============================================================
# 9. SELECT FEATURES
# ============================================================

FEATURES = [
    "sst",
    "sss",
    "ssh",
    "current_u",
    "current_v",
    "depth"
]

TARGET = "temperature"


print("Features:")

for feature in FEATURES:
    print(" -", feature)

print()

print("Target:")
print(" -", TARGET)

print()


# ============================================================
# 10. CREATE X AND Y
# ============================================================

X_train_full = train_df[FEATURES].values

y_train_full = train_df[TARGET].values

X_test = test_df[FEATURES].values

y_test = test_df[TARGET].values


# ============================================================
# 11. SAMPLE TRAINING DATA
# ============================================================

print("Preparing neural-network training data...")

if len(X_train_full) > MAX_TRAIN_SAMPLES:

    rng = np.random.default_rng(RANDOM_STATE)

    indices = rng.choice(
        len(X_train_full),
        size=MAX_TRAIN_SAMPLES,
        replace=False
    )

    X_train = X_train_full[indices]

    y_train = y_train_full[indices]

else:

    X_train = X_train_full

    y_train = y_train_full


print()

print("Full training records:", len(X_train_full))

print("Neural network samples:", len(X_train))

print("Test records:", len(X_test))

print()


# ============================================================
# 12. SCALE INPUT FEATURES
# ============================================================

print("Scaling input features...")

x_scaler = StandardScaler()

X_train_scaled = x_scaler.fit_transform(X_train)

X_test_scaled = x_scaler.transform(X_test)


# ============================================================
# 13. SCALE TARGET
# ============================================================

print("Scaling target temperature...")

y_scaler = StandardScaler()

y_train_scaled = y_scaler.fit_transform(
    y_train.reshape(-1, 1)
).ravel()


# ============================================================
# 14. CREATE NEURAL NETWORK
# ============================================================

print()

print("Creating neural network...")

print("Architecture:")

print("Input features :", len(FEATURES))

print("Hidden layer 1 : 64 neurons")

print("Hidden layer 2 : 32 neurons")

print("Output         : 1 temperature value")

print()


model = MLPRegressor(

    hidden_layer_sizes=HIDDEN_LAYERS,

    activation="relu",

    solver="adam",

    alpha=0.0001,

    batch_size=1024,

    learning_rate_init=0.001,

    max_iter=MAX_ITER,

    early_stopping=True,

    validation_fraction=0.10,

    n_iter_no_change=5,

    random_state=RANDOM_STATE,

    verbose=True
)


# ============================================================
# 15. TRAIN MODEL
# ============================================================

print("=" * 70)
print("TRAINING NEURAL NETWORK")
print("=" * 70)

print()

model.fit(
    X_train_scaled,
    y_train_scaled
)

print()

print("Training completed.")

print()

print("Iterations completed:", model.n_iter_)

print("Final loss:", model.loss_)

print()


# ============================================================
# 16. PREDICT
# ============================================================

print("=" * 70)
print("GENERATING PREDICTIONS")
print("=" * 70)

print()

pred_scaled = model.predict(
    X_test_scaled
)

pred_temperature = y_scaler.inverse_transform(
    pred_scaled.reshape(-1, 1)
).ravel()


# ============================================================
# 17. CALCULATE METRICS
# ============================================================

mae = mean_absolute_error(
    y_test,
    pred_temperature
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        pred_temperature
    )
)


print()

print("=" * 70)
print("STEP 32 RESULTS")
print("=" * 70)

print()

print(f"MAE  : {mae:.3f} °C")

print(f"RMSE : {rmse:.3f} °C")

print()


# ============================================================
# 18. COMPARE WITH STEP 31C
# ============================================================

STEP31C_MAE = 0.647

STEP31C_RMSE = 1.244

mae_change = STEP31C_MAE - mae

rmse_change = STEP31C_RMSE - rmse

mae_change_percent = (
    mae_change / STEP31C_MAE
) * 100

rmse_change_percent = (
    rmse_change / STEP31C_RMSE
) * 100


print("=" * 70)
print("COMPARISON WITH STEP 31C RANDOM FOREST")
print("=" * 70)

print()

print(f"31C MAE : {STEP31C_MAE:.3f} °C")

print(f"32 MAE  : {mae:.3f} °C")

print()

print(
    f"MAE change : {mae_change:.3f} °C"
)

print(
    f"MAE change % : {mae_change_percent:.2f}%"
)

print()

print(f"31C RMSE : {STEP31C_RMSE:.3f} °C")

print(f"32 RMSE  : {rmse:.3f} °C")

print()

print(
    f"RMSE change : {rmse_change:.3f} °C"
)

print(
    f"RMSE change % : {rmse_change_percent:.2f}%"
)

print()


# ============================================================
# 19. DEPTH-WISE ERROR
# ============================================================

print("=" * 70)
print("DEPTH-WISE PERFORMANCE")
print("=" * 70)

print()

test_results = test_df[
    [
        "date",
        "latitude",
        "longitude",
        "depth",
        "temperature"
    ]
].copy()

test_results["prediction"] = pred_temperature

test_results["absolute_error"] = (
    np.abs(
        test_results["temperature"]
        - test_results["prediction"]
    )
)


depth_results = []

for depth_value, group in test_results.groupby(
    "depth"
):

    depth_mae = group["absolute_error"].mean()

    depth_rmse = np.sqrt(
        np.mean(
            (
                group["temperature"]
                - group["prediction"]
            ) ** 2
        )
    )

    depth_results.append(
        {
            "depth": depth_value,
            "mae": depth_mae,
            "rmse": depth_rmse,
            "samples": len(group)
        }
    )


depth_results_df = pd.DataFrame(
    depth_results
).sort_values(
    "depth"
)


print(
    depth_results_df.to_string(
        index=False
    )
)

print()


# ============================================================
# 20. SAVE PREDICTIONS
# ============================================================

print("Saving predictions...")

test_results.to_csv(
    PREDICTIONS_FILE,
    index=False
)

print()

print("Predictions saved to:")

print(PREDICTIONS_FILE)

print()


# ============================================================
# 21. SAVE DEPTH ERROR
# ============================================================

depth_results_df.to_csv(
    DEPTH_ERROR_FILE,
    index=False
)

print("Depth-wise results saved to:")

print(DEPTH_ERROR_FILE)

print()


# ============================================================
# 22. SAVE COMPLETE MODEL PACKAGE
# ============================================================

print("Saving model...")

model_package = {

    "model": model,

    "x_scaler": x_scaler,

    "y_scaler": y_scaler,

    "features": FEATURES,

    "target": TARGET,

    "training_period": (
        "2020-01-01 to 2020-08-01"
    ),

    "testing_period": (
        "2020-09-01 to 2020-10-01"
    ),

    "mae": float(mae),

    "rmse": float(rmse),

    "random_state": RANDOM_STATE
}


joblib.dump(
    model_package,
    MODEL_FILE
)


print()

print("Model saved to:")

print(MODEL_FILE)

print()


# ============================================================
# 23. FINAL SUMMARY
# ============================================================

print("=" * 70)
print("STEP 32 COMPLETE")
print("=" * 70)

print()

print("Model:")
print("Lightweight depth-aware neural network")

print()

print("Training samples:")
print(len(X_train))

print()

print("Testing samples:")
print(len(X_test))

print()

print(f"MAE  : {mae:.3f} °C")

print(f"RMSE : {rmse:.3f} °C")

print()

print("Saved files:")

print("1.", MODEL_FILE)

print("2.", PREDICTIONS_FILE)

print("3.", DEPTH_ERROR_FILE)

print()

print("=" * 70)
print("DONE")
print("=" * 70)