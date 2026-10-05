import pandas as pd
from pathlib import Path

# Input files
temperature_file = "ml/data/real/glorys_temperature.csv"
surface_file = "ml/data/real/surface_inputs_demo.csv"

print("\nLoading GLORYS temperature data...")
temperature = pd.read_csv(temperature_file)

print("Loading surface input data...")
surface = pd.read_csv(surface_file)

# Convert GLORYS time column to date
temperature["date"] = pd.to_datetime(
    temperature["time"]
).dt.strftime("%Y-%m-%d")

# We will use the nearest available GLORYS depth
# for this first demonstration.
target_depth = 10.0

temperature["depth_difference"] = abs(
    temperature["depth"] - target_depth
)

# Select the GLORYS depth closest to 10 m
closest_depth = temperature["depth_difference"].min()

temperature_10m = temperature[
    temperature["depth_difference"] == closest_depth
].copy()

# Remove helper column
temperature_10m = temperature_10m.drop(
    columns=["depth_difference"]
)

# Rename temperature column
temperature_10m = temperature_10m.rename(
    columns={"temperature": "temperature_10m"}
)

# Keep only columns needed for joining
temperature_10m = temperature_10m[
    [
        "date",
        "latitude",
        "longitude",
        "temperature_10m"
    ]
]

print("\nGLORYS target depth selected:")
print(temperature_10m["temperature_10m"].head())

# Merge surface inputs with GLORYS temperature
combined = pd.merge(
    surface,
    temperature_10m,
    on=["date", "latitude", "longitude"],
    how="inner"
)

# Create output directory
Path("ml/data/real").mkdir(
    parents=True,
    exist_ok=True
)

# Save combined dataset
output_file = "ml/data/real/oceanembed_training_demo.csv"

combined.to_csv(
    output_file,
    index=False
)

print("\n===================================")
print("OCEANEMBED DATASET CREATED")
print("===================================")

print("\nNumber of records:")
print(len(combined))

print("\nColumns:")
print(list(combined.columns))

print("\nCombined dataset:")
print(combined)

print("\nSaved to:")
print(output_file)