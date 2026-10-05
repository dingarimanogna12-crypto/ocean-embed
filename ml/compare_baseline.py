import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


INPUT_FILE = "data/real/real_glorys_training.csv"


print("\n===================================")
print("OCEANEMBED BASELINE COMPARISON")
print("===================================")


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print("\nTotal records:", len(df))


# --------------------------------------------------
# REMOVE MISSING VALUES
# --------------------------------------------------

df = df.dropna(
    subset=[
        "depth",
        "sst",
        "sss",
        "ssh",
        "current_u",
        "current_v",
        "temperature"
    ]
)

print("Valid records:", len(df))


# --------------------------------------------------
# TRAIN / TEST SPLIT
# --------------------------------------------------

train_df, test_df = train_test_split(
    df,
    test_size=0.2,
    random_state=42
)


print("\nTraining records:", len(train_df))
print("Testing records:", len(test_df))


# ==================================================
# MODEL A — DEPTH ONLY
# ==================================================

print("\n===================================")
print("MODEL A — DEPTH ONLY")
print("===================================")

X_train_depth = train_df[
    ["depth"]
]

X_test_depth = test_df[
    ["depth"]
]

y_train = train_df[
    "temperature"
]

y_test = test_df[
    "temperature"
]


depth_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=25,
    random_state=42,
    n_jobs=-1
)


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


print(
    f"\nDepth-only MAE  : {depth_mae:.3f} °C"
)

print(
    f"Depth-only RMSE : {depth_rmse:.3f} °C"
)


# ==================================================
# MODEL B — OCEANEMBED
# ==================================================

print("\n===================================")
print("MODEL B — OCEANEMBED")
print("===================================")


features = [
    "sst",
    "sss",
    "ssh",
    "current_u",
    "current_v",
    "depth"
]


X_train_ocean = train_df[
    features
]

X_test_ocean = test_df[
    features
]


ocean_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=25,
    random_state=42,
    n_jobs=-1
)


print("\nTraining OceanEmbed model...")

ocean_model.fit(
    X_train_ocean,
    y_train
)


ocean_predictions = ocean_model.predict(
    X_test_ocean
)


ocean_mae = mean_absolute_error(
    y_test,
    ocean_predictions
)

ocean_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        ocean_predictions
    )
)


print(
    f"\nOceanEmbed MAE  : {ocean_mae:.3f} °C"
)

print(
    f"OceanEmbed RMSE : {ocean_rmse:.3f} °C"
)


# ==================================================
# IMPROVEMENT
# ==================================================

print("\n===================================")
print("MODEL COMPARISON")
print("===================================")


mae_improvement = (
    depth_mae - ocean_mae
)

rmse_improvement = (
    depth_rmse - ocean_rmse
)


print(
    f"\nMAE improvement  : "
    f"{mae_improvement:.3f} °C"
)

print(
    f"RMSE improvement : "
    f"{rmse_improvement:.3f} °C"
)


if depth_mae > 0:

    mae_percent = (
        mae_improvement /
        depth_mae
    ) * 100

else:

    mae_percent = 0


if depth_rmse > 0:

    rmse_percent = (
        rmse_improvement /
        depth_rmse
    ) * 100

else:

    rmse_percent = 0


print(
    f"\nMAE improvement percentage  : "
    f"{mae_percent:.2f}%"
)

print(
    f"RMSE improvement percentage : "
    f"{rmse_percent:.2f}%"
)


# ==================================================
# FINAL INTERPRETATION
# ==================================================

print("\n===================================")
print("INTERPRETATION")
print("===================================")


if ocean_mae < depth_mae:

    print(
        "\nSurface variables improve "
        "temperature reconstruction."
    )

else:

    print(
        "\nSurface variables do not improve "
        "the current model under this test."
    )


print(
    "\nImportant:"
)

print(
    "This experiment uses one GLORYS date "
    "and a limited 10-15N, 70-75E region."
)

print(
    "Therefore, these results are a "
    "prototype scientific baseline, "
    "not final OceanEmbed validation."
)


print("\n===================================")
print("STEP 30E COMPLETE")
print("===================================")