import pandas as pd
from pathlib import Path

# -----------------------------------------
# 1. Load GLORYS temperature data
# -----------------------------------------

glorys_file = "ml/data/real/glorys_temperature.csv"

print("\nLoading GLORYS data...")

glorys = pd.read_csv(glorys_file)

print("GLORYS records:", len(glorys))


# -----------------------------------------
# 2. Convert time to date
# -----------------------------------------

glorys["date"] = pd.to_datetime(
    glorys["time"]
).dt.strftime("%Y-%m-%d")


# -----------------------------------------
# 3. Select a useful depth
# -----------------------------------------

target_depth = 10.0

glorys["depth_difference"] = abs(
    glorys["depth"] - target_depth
)

closest_depth = glorys["depth_difference"].min()

glorys = glorys[
    glorys["depth_difference"] == closest_depth
].copy()

glorys = glorys.drop(
    columns=["depth_difference"]
)

glorys = glorys.rename(
    columns={
        "temperature": "temperature_10m"
    }
)


# -----------------------------------------
# 4. Create surface variables
# -----------------------------------------
# These are DEMO surface values.
# They are not real satellite measurements.

glorys["sst"] = (
    glorys["temperature_10m"] + 1.5
)

glorys["sss"] = 35.0

glorys["ssh"] = 0.35

glorys["current_u"] = 0.20

glorys["current_v"] = -0.10

glorys["wind_u"] = 4.0

glorys["wind_v"] = 2.0


# -----------------------------------------
# 5. Select final columns
# -----------------------------------------

training_data = glorys[
    [
        "date",
        "latitude",
        "longitude",
        "sst",
        "sss",
        "ssh",
        "current_u",
        "current_v",
        "wind_u",
        "wind_v",
        "temperature_10m"
    ]
]


# -----------------------------------------
# 6. Save expanded dataset
# -----------------------------------------

Path("ml/data/real").mkdir(
    parents=True,
    exist_ok=True
)

output_file = (
    "ml/data/real/"
    "oceanembed_training_demo.csv"
)

training_data.to_csv(
    output_file,
    index=False
)


# -----------------------------------------
# 7. Display results
# -----------------------------------------

print("\n===================================")
print("TRAINING DATA EXPANDED")
print("===================================")

print(
    "\nTotal training records:",
    len(training_data)
)

print("\nColumns:")
print(list(training_data.columns))

print("\nFirst 10 records:")
print(training_data.head(10))

print("\nSaved to:")
print(output_file)