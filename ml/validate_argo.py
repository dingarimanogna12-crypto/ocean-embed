import pandas as pd
import numpy as np
import joblib

from sklearn.metrics import mean_absolute_error, mean_squared_error


MODEL_FILE = "models/oceanembed_multidepth_model.pkl"

ARGO_FILE = "data/validation/argo_demo.csv"

OUTPUT_FILE = "data/validation/validation_results.csv"


DEPTHS = [
    0,
    5,
    10,
    20,
    30,
    50,
    75,
    100,
    125,
    150,
    200,
    300,
    500,
    700,
    1000
]


print("\n===================================")
print("OCEANEMBED ARGO VALIDATION")
print("===================================")


# Load model
print("\nLoading OceanEmbed model...")

model = joblib.load(MODEL_FILE)

print("Model loaded successfully!")


# Load ARGO reference data
print("\nLoading validation data...")

argo = pd.read_csv(ARGO_FILE)

print("Validation records:", len(argo))


# Surface input used for this demo
surface_input = {
    "sst": 28.4,
    "sss": 35.2,
    "ssh": 0.42,
    "current_u": 0.35,
    "current_v": -0.12,
    "wind_u": 4.2,
    "wind_v": 2.1
}


predictions = []


# Generate OceanEmbed predictions
for depth in DEPTHS:

    features = [[
        surface_input["sst"],
        surface_input["sss"],
        surface_input["ssh"],
        surface_input["current_u"],
        surface_input["current_v"],
        surface_input["wind_u"],
        surface_input["wind_v"],
        depth
    ]]

    prediction = model.predict(features)[0]

    predictions.append({
        "depth": depth,
        "oceanembed_temperature": float(prediction)
    })


prediction_df = pd.DataFrame(predictions)


# Match predictions with ARGO
comparison = pd.merge(
    argo,
    prediction_df,
    on="depth",
    how="inner"
)


# Calculate errors
comparison["error"] = (
    comparison["oceanembed_temperature"]
    - comparison["argo_temperature"]
)

comparison["absolute_error"] = (
    comparison["error"].abs()
)


# Metrics
mae = mean_absolute_error(
    comparison["argo_temperature"],
    comparison["oceanembed_temperature"]
)

rmse = np.sqrt(
    mean_squared_error(
        comparison["argo_temperature"],
        comparison["oceanembed_temperature"]
    )
)


# Save results
comparison.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n===================================")
print("VALIDATION RESULTS")
print("===================================")

print(f"\nValidation points: {len(comparison)}")

print(f"\nMAE  : {mae:.3f} °C")

print(f"RMSE : {rmse:.3f} °C")


print("\nDepth-wise comparison:")

print(
    comparison[
        [
            "depth",
            "argo_temperature",
            "oceanembed_temperature",
            "absolute_error"
        ]
    ].to_string(index=False)
)


print("\nResults saved to:")

print(OUTPUT_FILE)


print("\n===================================")
print("STEP 23 COMPLETE")
print("===================================")