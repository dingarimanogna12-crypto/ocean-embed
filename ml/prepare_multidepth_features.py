import pandas as pd
import numpy as np
from pathlib import Path

INPUT_FILE = "data/real/multidepth_training.csv"
OUTPUT_FILE = "data/real/multidepth_features.csv"

print("\n===================================")
print("CREATING MULTI-DEPTH ML FEATURES")
print("===================================")

df = pd.read_csv(INPUT_FILE)

print("\nInput records:", len(df))

# Create surface-style demo features.
# IMPORTANT: These are prototype/demo features,
# not real satellite measurements.

# Estimate SST using the shallowest temperature
surface_temperature = (
    df.groupby(["date", "latitude", "longitude"])["temperature"]
    .transform("max")
)

df["sst"] = surface_temperature

# Demo salinity field
df["sss"] = (
    35.0
    + 0.02 * np.sin(np.radians(df["latitude"]))
)

# Demo sea-surface height
df["ssh"] = (
    0.35
    + 0.001 * df["latitude"]
    - 0.001 * df["longitude"]
)

# Demo surface currents
df["current_u"] = (
    0.20
    + 0.01 * np.sin(np.radians(df["longitude"]))
)

df["current_v"] = (
    -0.10
    + 0.01 * np.cos(np.radians(df["latitude"]))
)

# Demo wind components
df["wind_u"] = (
    4.0
    + 0.05 * np.sin(np.radians(df["latitude"]))
)

df["wind_v"] = (
    2.0
    + 0.05 * np.cos(np.radians(df["longitude"]))
)

# Keep required columns
training_data = df[
    [
        "date",
        "latitude",
        "longitude",
        "depth",
        "sst",
        "sss",
        "ssh",
        "current_u",
        "current_v",
        "wind_u",
        "wind_v",
        "temperature",
    ]
]

Path("ml/data/real").mkdir(
    parents=True,
    exist_ok=True
)

training_data.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n===================================")
print("MULTI-DEPTH FEATURES CREATED")
print("===================================")

print("\nTotal records:", len(training_data))

print("\nColumns:")
print(list(training_data.columns))

print("\nFirst 10 records:")
print(training_data.head(10))

print("\nDepth count:")
print(training_data["depth"].nunique())

print("\nSaved to:")
print(OUTPUT_FILE)