import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ==========================================
# OCEANEMBED MULTI-DATE REAL MODEL
# ==========================================

INPUT_FILE = "data/real/multidate_real_training.csv"
MODEL_FILE = "models/oceanembed_multidate_model.pkl"


print("\n===================================")
print("OCEANEMBED MULTI-DATE REAL MODEL")
print("TRAINING")
print("===================================")


# ==========================================
# LOAD DATA
# ==========================================

print("\nLoading dataset...")

df = pd.read_csv(INPUT_FILE)

print("Total records:", len(df))


# ==========================================
# CHECK DATES
# ==========================================

df["date"] = pd.to_datetime(df["date"])

print("\nAvailable dates:")

for date in sorted(df["date"].unique()):
    print(" -", date.strftime("%Y-%m-%d"))


# ==========================================
# TEMPORAL TRAIN / TEST SPLIT
# ==========================================

# Training:
# January 2020 -> August 2020
#
# Testing:
# September 2020 -> October 2020

train_end = pd.Timestamp("2020-08-01")

train_df = df[
    df["date"] <= train_end
].copy()

test_df = df[
    df["date"] > train_end
].copy()


print("\n===================================")
print("TEMPORAL TRAIN / TEST SPLIT")
print("===================================")

print("\nTraining dates:")

for date in sorted(train_df["date"].unique()):
    print(" -", date.strftime("%Y-%m-%d"))

print("\nTesting dates:")

for date in sorted(test_df["date"].unique()):
    print(" -", date.strftime("%Y-%m-%d"))


print("\nTraining records:", len(train_df))
print("Testing records :", len(test_df))


# ==========================================
# FEATURES
# ==========================================

FEATURES = [
    "sst",
    "sss",
    "ssh",
    "current_u",
    "current_v",
    "depth",
]

TARGET = "temperature"


X_train = train_df[FEATURES]
y_train = train_df[TARGET]

X_test = test_df[FEATURES]
y_test = test_df[TARGET]


# ==========================================
# TRAIN MODEL
# ==========================================

print("\n===================================")
print("TRAINING RANDOM FOREST")
print("===================================")

model = RandomForestRegressor(
    n_estimators=100,
    max_depth=20,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
)

print("\nStarting training...")

model.fit(
    X_train,
    y_train
)

print("Training completed!")


# ==========================================
# PREDICTION
# ==========================================

print("\nGenerating predictions...")

predictions = model.predict(
    X_test
)


# ==========================================
# METRICS
# ==========================================

mae = mean_absolute_error(
    y_test,
    predictions
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)


print("\n===================================")
print("OCEANEMBED MULTI-DATE RESULTS")
print("===================================")

print(
    f"\nMAE  : {mae:.3f} °C"
)

print(
    f"RMSE : {rmse:.3f} °C"
)


# ==========================================
# FEATURE IMPORTANCE
# ==========================================

print("\n===================================")
print("FEATURE IMPORTANCE")
print("===================================")

importance = pd.DataFrame({
    "feature": FEATURES,
    "importance": model.feature_importances_,
})

importance = importance.sort_values(
    "importance",
    ascending=False
)

for _, row in importance.iterrows():

    print(
        f"{row['feature']:12s} : "
        f"{row['importance']:.6f}"
    )


# ==========================================
# ERROR BY DEPTH
# ==========================================

test_df["prediction"] = predictions

test_df["absolute_error"] = (
    test_df["temperature"]
    - test_df["prediction"]
).abs()


depth_error = (
    test_df
    .groupby("depth")["absolute_error"]
    .mean()
    .reset_index()
)

print("\n===================================")
print("ERROR BY DEPTH")
print("===================================")

print(
    depth_error.to_string(
        index=False
    )
)


# ==========================================
# SAVE MODEL
# ==========================================

Path("models").mkdir(
    parents=True,
    exist_ok=True
)

joblib.dump(
    model,
    MODEL_FILE
)


print("\n===================================")
print("MODEL SAVED")
print("===================================")

print(
    "\nLocation:",
    MODEL_FILE
)

print("\n===================================")
print("STEP 31C COMPLETE")
print("===================================")