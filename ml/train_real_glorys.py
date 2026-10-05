import pandas as pd
import numpy as np
import joblib

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


# --------------------------------------------------
# FILES
# --------------------------------------------------

INPUT_FILE = "data/real/real_glorys_training.csv"

MODEL_FILE = "models/oceanembed_real_glorys_model.pkl"


print("\n===================================")
print("OCEANEMBED REAL GLORYS MODEL")
print("===================================")


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

print("\nLoading real GLORYS training data...")

df = pd.read_csv(INPUT_FILE)

print("\nTotal records:", len(df))


# --------------------------------------------------
# FEATURES
# --------------------------------------------------

features = [
    "sst",
    "sss",
    "ssh",
    "current_u",
    "current_v",
    "depth"
]

target = "temperature"


print("\nFeatures:")
for feature in features:
    print(" -", feature)

print("\nTarget:")
print(" -", target)


# --------------------------------------------------
# PREPARE X AND Y
# --------------------------------------------------

X = df[features]

y = df[target]


# --------------------------------------------------
# TRAIN / TEST SPLIT
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))


# --------------------------------------------------
# TRAIN MODEL
# --------------------------------------------------

print("\nTraining real-data OceanEmbed model...")

model = RandomForestRegressor(
    n_estimators=100,
    max_depth=25,
    random_state=42,
    n_jobs=-1
)


model.fit(
    X_train,
    y_train
)


print("\nTraining completed!")


# --------------------------------------------------
# PREDICTIONS
# --------------------------------------------------

print("\nGenerating test predictions...")

predictions = model.predict(
    X_test
)


# --------------------------------------------------
# METRICS
# --------------------------------------------------

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


# --------------------------------------------------
# RESULTS
# --------------------------------------------------

print("\n===================================")
print("REAL GLORYS MODEL RESULTS")
print("===================================")

print(
    f"\nMAE  : {mae:.3f} °C"
)

print(
    f"RMSE : {rmse:.3f} °C"
)


# --------------------------------------------------
# SAVE MODEL
# --------------------------------------------------

Path("models").mkdir(
    parents=True,
    exist_ok=True
)


joblib.dump(
    model,
    MODEL_FILE
)


print("\nModel saved successfully!")

print("\nLocation:")
print(MODEL_FILE)


# --------------------------------------------------
# FEATURE IMPORTANCE
# --------------------------------------------------

print("\n===================================")
print("FEATURE IMPORTANCE")
print("===================================")

importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    "importance",
    ascending=False
)

print(
    importance.to_string(
        index=False
    )
)


# --------------------------------------------------
# DEPTH INFORMATION
# --------------------------------------------------

print("\n===================================")
print("DEPTH INFORMATION")
print("===================================")

print(
    "Minimum depth:",
    df["depth"].min(),
    "m"
)

print(
    "Maximum depth:",
    df["depth"].max(),
    "m"
)

print(
    "Depth levels:",
    df["depth"].nunique()
)


print("\n===================================")
print("STEP 30D COMPLETE")
print("===================================")