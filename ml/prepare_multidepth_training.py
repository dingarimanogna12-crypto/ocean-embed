import pandas as pd
from pathlib import Path

INPUT_FILE = "ml/data/real/glorys_temperature.csv"
OUTPUT_FILE = "ml/data/real/multidepth_training.csv"

print("\n===================================")
print("PREPARING MULTI-DEPTH GLORYS DATA")
print("===================================")

df = pd.read_csv(INPUT_FILE)

print("\nOriginal records:", len(df))

# Convert time to date
df["date"] = pd.to_datetime(df["time"]).dt.strftime("%Y-%m-%d")

# Keep required columns
df = df[
    [
        "date",
        "latitude",
        "longitude",
        "depth",
        "temperature",
    ]
]

# Remove missing temperatures
df = df.dropna(subset=["temperature"])

# Sort the dataset
df = df.sort_values(
    by=["date", "latitude", "longitude", "depth"]
)

Path("ml/data/real").mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nMulti-depth dataset created!")

print("\nTotal records:", len(df))

print("\nColumns:")
print(list(df.columns))

print("\nDepth levels:")
print(
    sorted(
        df["depth"].unique()
    )
)

print("\nFirst 10 records:")
print(df.head(10))

print("\nSaved to:")
print(OUTPUT_FILE)