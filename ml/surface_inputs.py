import pandas as pd
from pathlib import Path

# Demo surface observations
data = [
    {
        "date": "2020-01-01",
        "latitude": 10.0,
        "longitude": 70.0,
        "sst": 27.8,
        "sss": 35.1,
        "ssh": 0.35,
        "current_u": 0.20,
        "current_v": -0.10,
        "wind_u": 4.0,
        "wind_v": 2.0,
    },
    {
        "date": "2020-01-01",
        "latitude": 10.0,
        "longitude": 70.08,
        "sst": 27.9,
        "sss": 35.2,
        "ssh": 0.36,
        "current_u": 0.22,
        "current_v": -0.11,
        "wind_u": 4.1,
        "wind_v": 2.1,
    },
    {
        "date": "2020-01-01",
        "latitude": 10.08,
        "longitude": 70.0,
        "sst": 28.0,
        "sss": 35.0,
        "ssh": 0.34,
        "current_u": 0.21,
        "current_v": -0.09,
        "wind_u": 3.9,
        "wind_v": 1.9,
    },
]

df = pd.DataFrame(data)

# Create output folder
Path("ml/data/real").mkdir(parents=True, exist_ok=True)

# Save file
output_file = "ml/data/real/surface_inputs_demo.csv"

df.to_csv(output_file, index=False)

print("\n===================================")
print("SURFACE INPUT DATA CREATED")
print("===================================")

print("\nColumns:")
print(list(df.columns))

print("\nData:")
print(df)

print(f"\nSaved to:")
print(output_file)python ml/surface_inputs.py