import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ==========================================
# OCEANEMBED STEP 31E
# LIGHTWEIGHT PHYSICS-INFORMED EXPERIMENT
# ==========================================

INPUT_FILE = "data/real/multidate_real_training.csv"

MODEL_FILE = (
    "models/"
    "oceanembed_physics_features_model.pkl"
)

FEATURE_DATA_FILE = (
    "data/real/"
    "multidate_physics_features.csv"
)


print("\n===================================")
print("OCEANEMBED STEP 31E")
print("LIGHTWEIGHT PHYSICS-INFORMED MODEL")
print("===================================")


# ==========================================
# LOAD DATA
# ==========================================

print("\nLoading dataset...")

df = pd.read_csv(INPUT_FILE)

df["date"] = pd.to_datetime(df["date"])

print("Total records:", len(df))


# ==========================================
# CREATE PHYSICAL FEATURES
# ==========================================

print("\n===================================")
print("CREATING PHYSICAL FEATURES")
print("===================================")


df["current_speed"] = np.sqrt(
    df["current_u"] ** 2 +
    df["current_v"] ** 2
)


df["current_direction"] = np.arctan2(
    df["current_v"],
    df["current_u"]
)


df["depth_sst_interaction"] = (
    df["depth"] * df["sst"]
)


df["depth_ssh_interaction"] = (
    df["depth"] * df["ssh"]
)


df["surface_density_proxy"] = (
    df["sss"] -
    0.2 * df["sst"]
)


df["sst_sss_interaction"] = (
    df["sst"] * df["sss"]
)


print("\nCreated features:")

NEW_FEATURES = [
    "current_speed",
    "current_direction",
    "depth_sst_interaction",
    "depth_ssh_interaction",
    "surface_density_proxy",
    "sst_sss_interaction"
]

for feature in NEW_FEATURES:
    print(" -", feature)


# ==========================================
# TEMPORAL SPLIT
# ==========================================

print("\n===================================")
print("TEMPORAL TRAIN / TEST SPLIT")
print("===================================")


train_end = pd.Timestamp("2020-08-01")


train_df = df[
    df["date"] <= train_end
].copy()


test_df = df[
    df["date"] > train_end
].copy()


print(
    "\nFull training records:",
    len(train_df)
)

print(
    "Testing records:",
    len(test_df)
)


# ==========================================
# SAMPLE TRAINING DATA
# ==========================================

print("\n===================================")
print("CREATING LIGHTWEIGHT TRAINING SAMPLE")
print("===================================")


SAMPLE_SIZE = 100_000


if len(train_df) > SAMPLE_SIZE:

    train_sample = train_df.sample(
        n=SAMPLE_SIZE,
        random_state=42
    ).copy()

else:

    train_sample = train_df.copy()


print(
    "Training sample:",
    len(train_sample)
)

print(
    "Testing sample:",
    len(test_df)
)


# ==========================================
# FEATURES
# ==========================================

FEATURES = [
    "sst",
    "sss",
    "ssh",
    "current_u",
    "current_v",
    "current_speed",
    "current_direction",
    "depth",
    "depth_sst_interaction",
    "depth_ssh_interaction",
    "surface_density_proxy",
    "sst_sss_interaction"
]


TARGET = "temperature"


X_train = train_sample[FEATURES]

y_train = train_sample[TARGET]

X_test = test_df[FEATURES]

y_test = test_df[TARGET]


# ==========================================
# TRAIN MODEL
# ==========================================

print("\n===================================")
print("TRAINING LIGHTWEIGHT MODEL")
print("===================================")

print("\nRandom Forest:")
print("Trees          : 20")
print("Maximum depth  : 12")
print("Minimum samples: 5")
print("Training rows  :", len(train_sample))


model = RandomForestRegressor(
    n_estimators=20,
    max_depth=12,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1
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

print("Predictions generated!")


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
print("STEP 31E RESULTS")
print("===================================")

print(
    f"\nMAE  : {mae:.3f} °C"
)

print(
    f"RMSE : {rmse:.3f} °C"
)


# ==========================================
# COMPARE WITH STEP 31C
# ==========================================

OLD_MAE = 0.647

OLD_RMSE = 1.244


mae_change = OLD_MAE - mae

rmse_change = OLD_RMSE - rmse


mae_percent = (
    mae_change /
    OLD_MAE *
    100
)


rmse_percent = (
    rmse_change /
    OLD_RMSE *
    100
)


print("\n===================================")
print("COMPARISON WITH STEP 31C")
print("===================================")

print(
    f"\n31C MAE : {OLD_MAE:.3f} °C"
)

print(
    f"31E MAE : {mae:.3f} °C"
)

print(
    f"\nMAE change : {mae_change:.3f} °C"
)

print(
    f"MAE change % : {mae_percent:.2f}%"
)


print(
    f"\n31C RMSE : {OLD_RMSE:.3f} °C"
)

print(
    f"31E RMSE : {rmse:.3f} °C"
)

print(
    f"\nRMSE change : {rmse_change:.3f} °C"
)

print(
    f"RMSE change % : {rmse_percent:.2f}%"
)


# ==========================================
# FEATURE IMPORTANCE
# ==========================================

print("\n===================================")
print("FEATURE IMPORTANCE")
print("===================================")


importance = pd.DataFrame({
    "feature": FEATURES,
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


# ==========================================
# ERROR BY DEPTH
# ==========================================

print("\n===================================")
print("ERROR BY DEPTH")
print("===================================")


test_results = test_df[
    [
        "date",
        "latitude",
        "longitude",
        "depth",
        "temperature"
    ]
].copy()


test_results["prediction"] = predictions


test_results["absolute_error"] = (
    test_results["temperature"]
    - test_results["prediction"]
).abs()


depth_error = (
    test_results
    .groupby("depth")["absolute_error"]
    .mean()
    .reset_index()
)


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
    "Location:",
    MODEL_FILE
)


# ==========================================
# SAVE FEATURE DATA
# ==========================================

print("\nSaving feature dataset...")

df.to_csv(
    FEATURE_DATA_FILE,
    index=False
)


print(
    "Saved:",
    FEATURE_DATA_FILE
)


# ==========================================
# FINAL RESULT
# ==========================================

print("\n===================================")
print("STEP 31E COMPLETE")
print("===================================")


if mae < OLD_MAE:

    print(
        "\nRESULT:"
    )

    print(
        "Physics-informed features "
        "improved the MAE."
    )

elif mae > OLD_MAE:

    print(
        "\nRESULT:"
    )

    print(
        "Physics-informed features "
        "did not improve the MAE."
    )

else:

    print(
        "\nRESULT:"
    )

    print(
        "MAE remained approximately "
        "unchanged."
    )


if rmse < OLD_RMSE:

    print(
        "\nRMSE also improved."
    )

elif rmse > OLD_RMSE:

    print(
        "\nRMSE became worse."
    )

else:

    print(
        "\nRMSE remained approximately "
        "unchanged."
    )


print("\n===================================")