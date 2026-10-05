from pathlib import Path
import io
import requests
import numpy as np
import pandas as pd
import joblib

# ============================================================
# STEP 34 — REAL ARGO VALIDATION
# OceanEmbed
# ============================================================

print("\n==============================================")
print("STEP 34 — REAL ARGO VALIDATION")
print("==============================================")

# ------------------------------------------------------------
# 1. PATHS
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ARGO_DIR = PROJECT_ROOT / "ml" / "data" / "validation"
ARGO_DIR.mkdir(parents=True, exist_ok=True)

ARGO_FILE = ARGO_DIR / "argo_real.csv"

MODEL_FILE = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "oceanembed_step32_neural.pkl"
)

GLORYS_FILE = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "real"
    / "multidate_real_training.csv"
)

RESULT_FILE = (
    ARGO_DIR
    / "argo_validation_results.csv"
)

DEPTH_RESULT_FILE = (
    ARGO_DIR
    / "argo_depth_results.csv"
)

# ------------------------------------------------------------
# 2. REGION AND TIME
# ------------------------------------------------------------

LAT_MIN = 10.0
LAT_MAX = 15.0

LON_MIN = 70.0
LON_MAX = 75.0

START_DATE = "2020-01-01T00:00:00Z"
END_DATE = "2020-10-31T23:59:59Z"

MAX_DEPTH = 800.0


# ============================================================
# STEP 34A — DOWNLOAD REAL ARGO
# ============================================================

print("\nDownloading REAL ARGO data...")

BASE_URL = (
    "https://erddap.aoml.noaa.gov/hdb/erddap/"
    "tabledap/argo_float_indian_2017_2020.csv"
)

variables = ",".join([
    "time",
    "PLATFORM_NUMBER",
    "latitude",
    "longitude",
    "POSITION_QC",
    "PRES_ADJUSTED",
    "PRES_ADJUSTED_QC",
    "TEMP_ADJUSTED",
    "TEMP_ADJUSTED_QC",
    "PSAL_ADJUSTED",
    "PSAL_ADJUSTED_QC",
])

query = (
    f"{variables}"
    f"&time>={START_DATE}"
    f"&time<={END_DATE}"
    f"&latitude>={LAT_MIN}"
    f"&latitude<={LAT_MAX}"
    f"&longitude>={LON_MIN}"
    f"&longitude<={LON_MAX}"
    f"&PRES_ADJUSTED>=0"
    f"&PRES_ADJUSTED<={MAX_DEPTH}"
    f"&TEMP_ADJUSTED_QC=1"
    f"&PRES_ADJUSTED_QC=1"
)

URL = BASE_URL + "?" + query

try:
    response = requests.get(
        URL,
        timeout=300
    )
except requests.RequestException as error:
    print("\nERROR connecting to ARGO server:")
    print(error)
    raise SystemExit(1)

if response.status_code != 200:
    print("\nERROR downloading ARGO data")
    print("HTTP status:", response.status_code)
    print(response.text[:2000])
    raise SystemExit(1)

try:
    argo = pd.read_csv(
        io.StringIO(response.text)
    )
except Exception as error:
    print("\nERROR reading ARGO CSV:")
    print(error)
    print(response.text[:2000])
    raise SystemExit(1)

print("\nARGO download successful.")
print("Raw ARGO records:", len(argo))


# ============================================================
# STEP 34B — CLEAN ARGO
# ============================================================

print("\nCleaning ARGO data...")

argo.columns = [
    str(column).strip().lower()
    for column in argo.columns
]

print("\nARGO columns received:")

for column in argo.columns:
    print(" -", column)


# ------------------------------------------------------------
# Convert time
# ------------------------------------------------------------

argo["time"] = pd.to_datetime(
    argo["time"],
    errors="coerce",
    utc=True
)

numeric_columns = [
    "latitude",
    "longitude",
    "pres_adjusted",
    "temp_adjusted"
]

for column in numeric_columns:
    argo[column] = pd.to_numeric(
        argo[column],
        errors="coerce"
    )


# ------------------------------------------------------------
# Remove missing values
# ------------------------------------------------------------

argo = argo.dropna(
    subset=[
        "time",
        "latitude",
        "longitude",
        "pres_adjusted",
        "temp_adjusted"
    ]
)


# ------------------------------------------------------------
# Geographic filtering
# ------------------------------------------------------------

argo = argo[
    (argo["latitude"] >= LAT_MIN)
    &
    (argo["latitude"] <= LAT_MAX)
    &
    (argo["longitude"] >= LON_MIN)
    &
    (argo["longitude"] <= LON_MAX)
]


# ------------------------------------------------------------
# Depth filtering
# ------------------------------------------------------------

argo = argo[
    (argo["pres_adjusted"] >= 0)
    &
    (argo["pres_adjusted"] <= MAX_DEPTH)
]

print(
    "Clean ARGO records:",
    len(argo)
)

if len(argo) == 0:
    print("\nERROR: No valid ARGO observations.")
    raise SystemExit(1)


argo.to_csv(
    ARGO_FILE,
    index=False
)

print("\nSaved real ARGO data:")
print(ARGO_FILE)


# ============================================================
# STEP 34C — LOAD STEP 32 MODEL
# ============================================================

print("\nLoading OceanEmbed Step-32 model...")

if not MODEL_FILE.exists():
    print("\nERROR: Model not found:")
    print(MODEL_FILE)
    raise SystemExit(1)

model_data = joblib.load(
    MODEL_FILE
)

print(
    "Saved model object type:",
    type(model_data)
)


# ------------------------------------------------------------
# IMPORTANT FIX
# Step 32 saved a dictionary containing
# the actual model and scalers.
# ------------------------------------------------------------

if isinstance(model_data, dict):

    print("\nModel file contains a dictionary.")

    print(
        "Available keys:"
    )

    for key in model_data.keys():
        print(
            " -",
            key
        )

    # Try common model key names
    possible_model_keys = [
        "model",
        "mlp",
        "regressor",
        "neural_model",
        "estimator"
    ]

    model = None

    for key in possible_model_keys:

        if key in model_data:

            candidate = model_data[key]

            if hasattr(
                candidate,
                "predict"
            ):

                model = candidate

                print(
                    "\nUsing model stored under key:",
                    key
                )

                break


    # If no common key worked,
    # search all dictionary values.
    if model is None:

        for key, value in model_data.items():

            if hasattr(
                value,
                "predict"
            ):

                model = value

                print(
                    "\nFound prediction model under key:",
                    key
                )

                break


    if model is None:

        print(
            "\nERROR: Could not find a "
            "prediction model inside the dictionary."
        )

        raise SystemExit(1)


else:

    model = model_data


if not hasattr(
    model,
    "predict"
):

    print(
        "\nERROR: Loaded object does not "
        "support predict()."
    )

    raise SystemExit(1)


print(
    "\nOceanEmbed model loaded successfully."
)


# ------------------------------------------------------------
# Check whether scaler exists
# ------------------------------------------------------------

x_scaler = None
y_scaler = None

if isinstance(model_data, dict):

    possible_x_scaler_keys = [
        "x_scaler",
        "scaler_x",
        "feature_scaler",
        "input_scaler"
    ]

    possible_y_scaler_keys = [
        "y_scaler",
        "scaler_y",
        "target_scaler",
        "output_scaler"
    ]

    for key in possible_x_scaler_keys:

        if key in model_data:

            x_scaler = model_data[key]

            print(
                "Input scaler found:",
                key
            )

            break

    for key in possible_y_scaler_keys:

        if key in model_data:

            y_scaler = model_data[key]

            print(
                "Target scaler found:",
                key
            )

            break


# ============================================================
# STEP 34D — LOAD GLORYS
# ============================================================

print("\nLoading GLORYS data...")

if not GLORYS_FILE.exists():

    print(
        "\nERROR: GLORYS dataset not found:"
    )

    print(GLORYS_FILE)

    raise SystemExit(1)


glorys = pd.read_csv(
    GLORYS_FILE,
    parse_dates=["date"]
)

print(
    "GLORYS records:",
    len(glorys)
)


# ------------------------------------------------------------
# Surface layer
# ------------------------------------------------------------

surface = glorys[
    glorys["depth"] <= 1.0
].copy()


surface["date_only"] = (
    pd.to_datetime(
        surface["date"]
    ).dt.date
)

argo["date_only"] = (
    argo["time"].dt.date
)


print(
    "GLORYS surface records:",
    len(surface)
)


# ============================================================
# STEP 34E — MATCH ARGO WITH GLORYS
# ============================================================

print(
    "\nMatching ARGO observations "
    "with GLORYS surface conditions..."
)


surface_by_date = {
    date_value: group
    for date_value, group
    in surface.groupby(
        "date_only"
    )
}


matched_rows = []


for date_value, argo_group in argo.groupby(
    "date_only"
):

    if date_value not in surface_by_date:
        continue

    grid = surface_by_date[
        date_value
    ]

    grid_lat = (
        grid["latitude"]
        .to_numpy()
    )

    grid_lon = (
        grid["longitude"]
        .to_numpy()
    )


    for _, obs in argo_group.iterrows():

        distance = (
            (grid_lat - obs["latitude"]) ** 2
            +
            (grid_lon - obs["longitude"]) ** 2
        )

        nearest_index = np.argmin(
            distance
        )

        matched = grid.iloc[
            nearest_index
        ]

        matched_rows.append({

            "time": obs["time"],

            "platform_number": obs.get(
                "platform_number",
                np.nan
            ),

            "argo_latitude":
                obs["latitude"],

            "argo_longitude":
                obs["longitude"],

            "argo_depth":
                obs["pres_adjusted"],

            "argo_temperature":
                obs["temp_adjusted"],

            "glorys_latitude":
                matched["latitude"],

            "glorys_longitude":
                matched["longitude"],

            "sst":
                matched["sst"],

            "sss":
                matched["sss"],

            "ssh":
                matched["ssh"],

            "current_u":
                matched["current_u"],

            "current_v":
                matched["current_v"]
        })


matched = pd.DataFrame(
    matched_rows
)


print(
    "Matched ARGO observations:",
    len(matched)
)


if len(matched) == 0:

    print(
        "\nERROR: No matching observations."
    )

    raise SystemExit(1)


# ============================================================
# STEP 34F — CLEAN MATCHED DATA
# ============================================================

required_columns = [
    "sst",
    "sss",
    "ssh",
    "current_u",
    "current_v",
    "argo_depth",
    "argo_temperature"
]

matched = matched.dropna(
    subset=required_columns
)


print(
    "Valid matched observations:",
    len(matched)
)


# ============================================================
# STEP 34G — PREPARE MODEL INPUT
# ============================================================

print(
    "\nPreparing OceanEmbed inputs..."
)


X = matched[
    [
        "sst",
        "sss",
        "ssh",
        "current_u",
        "current_v",
        "argo_depth"
    ]
].copy()


X = X.rename(
    columns={
        "argo_depth": "depth"
    }
)


# ------------------------------------------------------------
# Apply input scaler if Step 32 saved one
# ------------------------------------------------------------

if x_scaler is not None:

    print(
        "Applying Step-32 input scaler..."
    )

    X_model = x_scaler.transform(
        X
    )

else:

    print(
        "No input scaler found."
    )

    X_model = X


# ============================================================
# STEP 34H — PREDICT
# ============================================================

print(
    "\nRunning OceanEmbed predictions..."
)


predicted = model.predict(
    X_model
)


# ------------------------------------------------------------
# Convert predictions back if y scaler exists
# ------------------------------------------------------------

predicted = np.asarray(
    predicted
).reshape(-1, 1)


if y_scaler is not None:

    print(
        "Applying Step-32 target inverse scaler..."
    )

    predicted = y_scaler.inverse_transform(
        predicted
    )


predicted = predicted.ravel()


matched[
    "oceanembed_temperature"
] = predicted


# ============================================================
# STEP 34I — CALCULATE ERRORS
# ============================================================

matched["error"] = (
    matched["oceanembed_temperature"]
    -
    matched["argo_temperature"]
)


matched["absolute_error"] = (
    matched["error"].abs()
)


matched["squared_error"] = (
    matched["error"] ** 2
)


mae = (
    matched["absolute_error"]
    .mean()
)


rmse = np.sqrt(
    matched["squared_error"]
    .mean()
)


bias = (
    matched["error"]
    .mean()
)


# ============================================================
# STEP 34J — RESULTS
# ============================================================

print("\n==============================================")
print("STEP 34 — REAL ARGO RESULTS")
print("==============================================")


print(
    f"\nValidation observations : "
    f"{len(matched):,}"
)

print(
    f"MAE                    : "
    f"{mae:.3f} °C"
)

print(
    f"RMSE                   : "
    f"{rmse:.3f} °C"
)

print(
    f"Bias                   : "
    f"{bias:.3f} °C"
)


# ============================================================
# STEP 34K — DEPTH-WISE RESULTS
# ============================================================

print(
    "\nCalculating depth-wise validation..."
)


matched["depth_bin"] = (
    np.floor(
        matched["argo_depth"] / 25
    )
    * 25
)


depth_results = (
    matched
    .groupby("depth_bin")
    .agg(
        observations=(
            "absolute_error",
            "count"
        ),

        MAE=(
            "absolute_error",
            "mean"
        ),

        RMSE=(
            "squared_error",
            lambda x:
                np.sqrt(x.mean())
        ),

        bias=(
            "error",
            "mean"
        )
    )
    .reset_index()
)


print(
    "\nDepth-wise ARGO validation:"
)

print(
    depth_results.to_string(
        index=False
    )
)


# ============================================================
# STEP 34L — SAVE RESULTS
# ============================================================

matched.to_csv(
    RESULT_FILE,
    index=False
)


depth_results.to_csv(
    DEPTH_RESULT_FILE,
    index=False
)


print(
    "\nSaved validation results:"
)

print(
    RESULT_FILE
)


print(
    "\nSaved depth-wise results:"
)

print(
    DEPTH_RESULT_FILE
)


# ============================================================
# STEP 34 COMPLETE
# ============================================================

print("\n==============================================")
print("STEP 34 COMPLETE")
print("==============================================")


print(
    f"\nARGO observations : "
    f"{len(matched):,}"
)

print(
    f"MAE               : "
    f"{mae:.3f} °C"
)

print(
    f"RMSE              : "
    f"{rmse:.3f} °C"
)

print(
    f"Bias              : "
    f"{bias:.3f} °C"
)

print(
    "\nReal ARGO validation finished successfully."
)