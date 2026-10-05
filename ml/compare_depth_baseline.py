import pandas as pd
import numpy as np
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ==========================================
# OCEANEMBED STEP 31D
# DEPTH-ONLY BASELINE COMPARISON
# ==========================================

INPUT_FILE = "data/real/multidate_real_training.csv"
MODEL_FILE = "models/oceanembed_multidate_model.pkl"

print("\n===================================")
print("OCEANEMBED STEP 31D")
print("DEPTH-ONLY BASELINE COMPARISON")
print("===================================")


# ==========================================
# LOAD DATA
# ==========================================

print("\nLoading dataset...")

df = pd.read_csv(INPUT_FILE)

df["date"] = pd.to_datetime(df["date"])

print("Total records:", len(df))


# ==========================================
# SAME TEST PERIOD AS STEP 31C
# ==========================================

test_start = pd.Timestamp("2020-09-01")

test_df = df[
    df["date"] >= test_start
].copy()

print("\n===================================")
print("TEST DATA")
print("===================================")

print("Testing records:", len(test_df))

print(
    "\nTesting period:",
    test_df["date"].min().strftime("%Y-%m-%d"),
    "to",
    test_df["date"].max().strftime("%Y-%m-%d")
)


# ==========================================
# DEPTH-ONLY BASELINE
# ==========================================

print("\n===================================")
print("BASELINE: DEPTH ONLY")
print("===================================")

# Use a smaller model because this is
# only a baseline experiment.

depth_model = RandomForestRegressor(
    n_estimators=50,
    max_depth=20,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)


# Need training data only from Jan-Aug

train_end = pd.Timestamp("2020-08-01")

train_df = df[
    df["date"] <= train_end
].copy()


X_train_depth = train_df[["depth"]]
y_train = train_df["temperature"]

X_test_depth = test_df[["depth"]]
y_test = test_df["temperature"]


print("\nTraining depth-only model...")

depth_model.fit(
    X_train_depth,
    y_train
)


depth_predictions = depth_model.predict(
    X_test_depth
)


depth_mae = mean_absolute_error(
    y_test,
    depth_predictions
)

depth_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        depth_predictions
    )
)


print("\nDepth-only results:")

print(
    f"MAE  : {depth_mae:.3f} °C"
)

print(
    f"RMSE : {depth_rmse:.3f} °C"
)


# ==========================================
# LOAD EXISTING OCEANEMBED MODEL
# ==========================================

print("\n===================================")
print("OCEANEMBED MODEL")
print("===================================")

print("\nLoading Step 31C model...")

oceanembed_model = joblib.load(
    MODEL_FILE
)

print("Model loaded successfully.")


# ==========================================
# OCEANEMBED PREDICTIONS
# ==========================================

FEATURES = [
    "sst",
    "sss",
    "ssh",
    "current_u",
    "current_v",
    "depth"
]


X_test_full = test_df[FEATURES]


print("\nGenerating OceanEmbed predictions...")

oceanembed_predictions = (
    oceanembed_model.predict(
        X_test_full
    )
)


oceanembed_mae = mean_absolute_error(
    y_test,
    oceanembed_predictions
)

oceanembed_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        oceanembed_predictions
    )
)


print("\nOceanEmbed results:")

print(
    f"MAE  : {oceanembed_mae:.3f} °C"
)

print(
    f"RMSE : {oceanembed_rmse:.3f} °C"
)


# ==========================================
# IMPROVEMENT
# ==========================================

mae_improvement = (
    depth_mae - oceanembed_mae
)

rmse_improvement = (
    depth_rmse - oceanembed_rmse
)


mae_percent = (
    mae_improvement
    / depth_mae
    * 100
)

rmse_percent = (
    rmse_improvement
    / depth_rmse
    * 100
)


print("\n===================================")
print("SURFACE VARIABLE IMPROVEMENT")
print("===================================")

print(
    f"\nMAE improvement  : "
    f"{mae_improvement:.3f} °C"
)

print(
    f"MAE improvement %: "
    f"{mae_percent:.2f}%"
)

print(
    f"\nRMSE improvement  : "
    f"{rmse_improvement:.3f} °C"
)

print(
    f"RMSE improvement %: "
    f"{rmse_percent:.2f}%"
)


# ==========================================
# DEPTH-WISE COMPARISON
# ==========================================

test_results = test_df[
    [
        "date",
        "latitude",
        "longitude",
        "depth",
        "temperature"
    ]
].copy()


test_results["depth_prediction"] = (
    depth_predictions
)

test_results["oceanembed_prediction"] = (
    oceanembed_predictions
)


test_results["depth_error"] = (
    test_results["temperature"]
    - test_results["depth_prediction"]
).abs()


test_results["oceanembed_error"] = (
    test_results["temperature"]
    - test_results["oceanembed_prediction"]
).abs()


depth_comparison = (
    test_results
    .groupby("depth")
    .agg(
        depth_only_mae=(
            "depth_error",
            "mean"
        ),
        oceanembed_mae=(
            "oceanembed_error",
            "mean"
        )
    )
    .reset_index()
)


depth_comparison["improvement"] = (
    depth_comparison["depth_only_mae"]
    - depth_comparison["oceanembed_mae"]
)


print("\n===================================")
print("ERROR COMPARISON BY DEPTH")
print("===================================")

print(
    depth_comparison.to_string(
        index=False
    )
)


# ==========================================
# SAVE RESULTS
# ==========================================

output_file = (
    "data/real/"
    "depth_baseline_comparison.csv"
)

depth_comparison.to_csv(
    output_file,
    index=False
)


print("\n===================================")
print("RESULT SAVED")
print("===================================")

print(
    "Saved:",
    output_file
)


# ==========================================
# FINAL SUMMARY
# ==========================================

print("\n===================================")
print("STEP 31D COMPLETE")
print("===================================")

print(
    "\nDepth-only MAE:",
    f"{depth_mae:.3f} °C"
)

print(
    "OceanEmbed MAE:",
    f"{oceanembed_mae:.3f} °C"
)

print(
    "\nDepth-only RMSE:",
    f"{depth_rmse:.3f} °C"
)

print(
    "OceanEmbed RMSE:",
    f"{oceanembed_rmse:.3f} °C"
)

print("\n===================================")