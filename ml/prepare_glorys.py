import xarray as xr
import pandas as pd
from pathlib import Path

# Real GLORYS file
input_file = "ml/data/real/test_glorys.nc"

# Output file
output_file = "ml/data/real/glorys_temperature.csv"

print("\nOpening GLORYS dataset...")

# Open NetCDF file
ds = xr.open_dataset(input_file)

# Select ocean temperature
temperature = ds["thetao"]

# Convert to table
df = temperature.to_dataframe(name="temperature").reset_index()

# Remove missing temperature values
df = df.dropna(subset=["temperature"])

# Save as CSV
Path("ml/data/real").mkdir(parents=True, exist_ok=True)

df.to_csv(output_file, index=False)

print("\n===================================")
print("GLORYS DATA PREPARATION COMPLETE")
print("===================================")

print(f"\nTotal records: {len(df)}")

print("\nColumns:")
print(list(df.columns))

print("\nFirst 10 records:")
print(df.head(10))

print("\nTemperature statistics:")
print(df["temperature"].describe())

print(f"\nSaved successfully to:")
print(output_file)