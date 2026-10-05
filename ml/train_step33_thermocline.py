# ============================================================
# OCEANEMBED STEP 33
# THERMOCLINE-AWARE NEURAL NETWORK
# ============================================================

import sys
import joblib
import numpy as np
import pandas as pd

from pathlib import Path

from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ============================================================
# 1. PROJECT PATHS
# ============================================================

CURRENT_FILE = Path(__file__).resolve()

PROJECT_ROOT = CURRENT_FILE.parent.parent

DATA_FILE = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "real"
    / "multidate_real_training.csv"
)

MODEL_DIR = PROJECT_ROOT / "ml" / "models"

OUTPUT_DIR = PROJECT_ROOT / "data" / "real"

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

MODEL_FILE = (
    MODEL_DIR
    / "oceanembed_step33_thermocline.pkl"
)

PREDICTIONS_FILE = (
    OUTPUT_DIR
    / "step33_thermocline_predictions.csv"
)

DEPTH_ERROR_FILE = (
    OUTPUT_DIR
    / "step33_thermocline_depth_error.csv"
)


# ============================================================
# 2. SETTINGS
# ============================================================

RANDOM_STATE = 42

MAX_TRAIN_SAMPLES = 150_000

HIDDEN_LAYERS = (64, 32)

MAX_ITER = 35


# ============================================================
# 3. THERMOCLINE DEPTH RANGE
# ============================================================

THERMOCLINE_MIN = 40.0

THERMOCLINE_MAX = 130.0


# ============================================================
# 4. PRINT HEADER
# ============================================================

print("=" * 70)

print("OCEANEMBED STEP 33")

print("THERMOCLINE-AWARE NEURAL NETWORK")

print("=" * 70)

print()

print("Project root:")

print(PROJECT_ROOT)

print()

print("Dataset:")

print(DATA_FILE)

print()


# ============================================================
# 5. CHECK DATASET
# ============================================================

if not DATA_FILE.exists():

    print("ERROR: Dataset not found.")

    print()

    print("Expected:")

    print(DATA_FILE)

    sys.exit(1)


print("Dataset found successfully.")

print()


# ============================================================
# 6. LOAD DATASET
# ============================================================

print("Loading dataset...")

df = pd.read_csv(
    DATA_FILE
)

print("Dataset loaded.")

print()

print("Records:", len(df))

print()


# ============================================================
# 7. CHECK COLUMNS
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


missing = [

    c
    for c in required_columns
    if c not in df.columns

]


if missing:

    print("ERROR: Missing columns:")

    for c in missing:

        print("-", c)

    sys.exit(1)


# ============================================================
# 8. CLEAN DATA
# ============================================================

print("Cleaning data...")

df["date"] = pd.to_datetime(
    df["date"]
)

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

print(
    "Removed rows:",
    before - after
)

print(
    "Remaining rows:",
    after
)

print()


# ============================================================
# 9. TEMPORAL TRAIN / TEST SPLIT
# ============================================================

print("Creating temporal split...")

train_mask = (
    df["date"]
    < pd.Timestamp("2020-09-01")
)

test_mask = (
    df["date"]
    >= pd.Timestamp("2020-09-01")
)


train_df = df.loc[
    train_mask
].copy()


test_df = df.loc[
    test_mask
].copy()


print()

print(
    "Training records:",
    len(train_df)
)

print(
    "Testing records:",
    len(test_df)
)

print()


# ============================================================
# 10. FEATURES
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


# ============================================================
# 11. CREATE TRAIN / TEST ARRAYS
# ============================================================

X_train_full = train_df[
    FEATURES
].values


y_train_full = train_df[
    TARGET
].values


X_test = test_df[
    FEATURES
].values


y_test = test_df[
    TARGET
].values


# ============================================================
# 12. SAMPLE TRAINING DATA
# ============================================================

print("Preparing training samples...")

if len(X_train_full) > MAX_TRAIN_SAMPLES:

    rng = np.random.default_rng(
        RANDOM_STATE
    )

    indices = rng.choice(

        len(X_train_full),

        size=MAX_TRAIN_SAMPLES,

        replace=False

    )

    X_train = X_train_full[
        indices
    ]

    y_train = y_train_full[
        indices
    ]

else:

    X_train = X_train_full

    y_train = y_train_full


print()

print(
    "Full training records:",
    len(X_train_full)
)

print(
    "Selected training records:",
    len(X_train)
)

print()


# ============================================================
# 13. CREATE THERMOCLINE WEIGHTS
# ============================================================

print("=" * 70)

print("CREATING THERMOCLINE WEIGHTS")

print("=" * 70)

print()


train_depths = X_train[:, 5]


weights = np.ones(
    len(train_depths)
)


# Stronger weight in 40-130m

thermocline_mask = (

    (train_depths >= THERMOCLINE_MIN)

    &

    (train_depths <= THERMOCLINE_MAX)

)


weights[
    thermocline_mask
] = 3.0


print(
    "Normal samples:",
    np.sum(~thermocline_mask)
)

print(
    "Thermocline samples:",
    np.sum(thermocline_mask)
)

print()

print(
    "Thermocline weight: 3.0"
)

print(
    "Normal weight: 1.0"
)

print()


# ============================================================
# 14. SCALE INPUT
# ============================================================

print("Scaling input features...")

x_scaler = StandardScaler()

X_train_scaled = (
    x_scaler.fit_transform(
        X_train
    )
)


X_test_scaled = (
    x_scaler.transform(
        X_test
    )
)


# ============================================================
# 15. SCALE TARGET
# ============================================================

print("Scaling target...")

y_scaler = StandardScaler()

y_train_scaled = (
    y_scaler.fit_transform(
        y_train.reshape(-1, 1)
    ).ravel()
)


# ============================================================
# 16. CREATE NEURAL NETWORK
# ============================================================

print()

print("=" * 70)

print("CREATING THERMOCLINE-AWARE NETWORK")

print("=" * 70)

print()

print("Input features:", len(FEATURES))

print("Hidden layer 1: 64")

print("Hidden layer 2: 32")

print("Output: temperature")

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

    n_iter_no_change=6,

    random_state=RANDOM_STATE,

    verbose=True

)


# ============================================================
# 17. TRAIN
# ============================================================

print()

print("=" * 70)

print("TRAINING STEP 33")

print("=" * 70)

print()


# ------------------------------------------------------------
# IMPORTANT
# ------------------------------------------------------------
# MLPRegressor does not support sample_weight in all
# scikit-learn versions.
#
# Therefore we create a weighted training set by repeating
# thermocline samples.
# ------------------------------------------------------------

thermo_indices = np.where(
    thermocline_mask
)[0]


if len(thermo_indices) > 0:

    X_thermo = X_train_scaled[
        thermo_indices
    ]

    y_thermo = y_train_scaled[
        thermo_indices
    ]


    # Repeat thermocline samples twice
    X_extra = np.vstack(
        [
            X_thermo,
            X_thermo
        ]
    )


    y_extra = np.concatenate(
        [
            y_thermo,
            y_thermo
        ]
    )


    X_train_weighted = np.vstack(
        [
            X_train_scaled,
            X_extra
        ]
    )


    y_train_weighted = np.concatenate(
        [
            y_train_scaled,
            y_extra
        ]
    )

else:

    X_train_weighted = X_train_scaled

    y_train_weighted = y_train_scaled


print(
    "Original training samples:",
    len(X_train_scaled)
)

print(
    "Weighted training samples:",
    len(X_train_weighted)
)

print()


# ============================================================
# 18. TRAIN MODEL
# ============================================================

model.fit(

    X_train_weighted,

    y_train_weighted

)


print()

print("Training completed.")

print()

print(
    "Iterations:",
    model.n_iter_
)

print(
    "Final loss:",
    model.loss_
)

print()


# ============================================================
# 19. PREDICT
# ============================================================

print("=" * 70)

print("GENERATING PREDICTIONS")

print("=" * 70)

print()


prediction_scaled = model.predict(

    X_test_scaled

)


pred_temperature = (
    y_scaler.inverse_transform(
        prediction_scaled.reshape(-1, 1)
    ).ravel()
)


# ============================================================
# 20. OVERALL METRICS
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

print("STEP 33 RESULTS")

print("=" * 70)

print()

print(
    f"MAE  : {mae:.3f} °C"
)

print(
    f"RMSE : {rmse:.3f} °C"
)

print()


# ============================================================
# 21. STEP 32 COMPARISON
# ============================================================

STEP32_MAE = 0.650

STEP32_RMSE = 1.099


mae_change = (
    STEP32_MAE - mae
)


rmse_change = (
    STEP32_RMSE - rmse
)


mae_percent = (
    mae_change
    / STEP32_MAE
) * 100


rmse_percent = (
    rmse_change
    / STEP32_RMSE
) * 100


print("=" * 70)

print("COMPARISON WITH STEP 32")

print("=" * 70)

print()

print(
    f"Step 32 MAE : {STEP32_MAE:.3f} °C"
)

print(
    f"Step 33 MAE : {mae:.3f} °C"
)

print()

print(
    f"MAE change : {mae_change:.3f} °C"
)

print(
    f"MAE change % : {mae_percent:.2f}%"
)

print()

print(
    f"Step 32 RMSE : {STEP32_RMSE:.3f} °C"
)

print(
    f"Step 33 RMSE : {rmse:.3f} °C"
)

print()

print(
    f"RMSE change : {rmse_change:.3f} °C"
)

print(
    f"RMSE change % : {rmse_percent:.2f}%"
)

print()


# ============================================================
# 22. DEPTH-WISE RESULTS
# ============================================================

print("=" * 70)

print("DEPTH-WISE PERFORMANCE")

print("=" * 70)

print()


results = test_df[
    [
        "date",

        "latitude",

        "longitude",

        "depth",

        "temperature"

    ]
].copy()


results["prediction"] = (
    pred_temperature
)


results["absolute_error"] = np.abs(

    results["temperature"]

    -

    results["prediction"]

)


depth_results = []


for depth_value, group in results.groupby(
    "depth"
):

    depth_mae = (
        group["absolute_error"]
        .mean()
    )


    depth_rmse = np.sqrt(

        np.mean(

            (
                group["temperature"]

                -

                group["prediction"]

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
# 23. THERMOCLINE-ONLY PERFORMANCE
# ============================================================

thermo_results = results[
    (
        results["depth"]
        >= THERMOCLINE_MIN
    )

    &

    (
        results["depth"]
        <= THERMOCLINE_MAX
    )
]


thermo_mae = (
    thermo_results[
        "absolute_error"
    ].mean()
)


thermo_rmse = np.sqrt(

    np.mean(

        (
            thermo_results[
                "temperature"
            ]

            -

            thermo_results[
                "prediction"
            ]

        ) ** 2

    )

)


print("=" * 70)

print("THERMOCLINE-ONLY PERFORMANCE")

print("=" * 70)

print()

print(
    f"Thermocline MAE  : {thermo_mae:.3f} °C"
)

print(
    f"Thermocline RMSE : {thermo_rmse:.3f} °C"
)

print(
    "Depth range      : 40–130 m"
)

print()


# ============================================================
# 24. SAVE PREDICTIONS
# ============================================================

results.to_csv(

    PREDICTIONS_FILE,

    index=False

)


print(
    "Predictions saved:"
)

print(
    PREDICTIONS_FILE
)

print()


# ============================================================
# 25. SAVE DEPTH RESULTS
# ============================================================

depth_results_df.to_csv(

    DEPTH_ERROR_FILE,

    index=False

)


print(
    "Depth results saved:"
)

print(
    DEPTH_ERROR_FILE
)

print()


# ============================================================
# 26. SAVE MODEL
# ============================================================

model_package = {

    "model": model,

    "x_scaler": x_scaler,

    "y_scaler": y_scaler,

    "features": FEATURES,

    "target": TARGET,

    "thermocline_min": THERMOCLINE_MIN,

    "thermocline_max": THERMOCLINE_MAX,

    "thermocline_weight": 3.0,

    "mae": float(mae),

    "rmse": float(rmse),

    "thermocline_mae": float(
        thermo_mae
    ),

    "thermocline_rmse": float(
        thermo_rmse
    ),

    "random_state": RANDOM_STATE

}


joblib.dump(

    model_package,

    MODEL_FILE

)


print()

print(
    "Model saved:"
)

print(
    MODEL_FILE
)

print()


# ============================================================
# 27. FINAL MESSAGE
# ============================================================

print("=" * 70)

print("STEP 33 COMPLETE")

print("=" * 70)

print()

print(
    f"Overall MAE  : {mae:.3f} °C"
)

print(
    f"Overall RMSE : {rmse:.3f} °C"
)

print()

print(
    f"Thermocline MAE  : {thermo_mae:.3f} °C"
)

print(
    f"Thermocline RMSE : {thermo_rmse:.3f} °C"
)

print()

print(
    "The key question is whether the"
)

print(
    "40–130 m errors improved."
)

print()

print("=" * 70)