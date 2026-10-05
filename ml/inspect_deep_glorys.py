import xarray as xr
from pathlib import Path

DATA_FOLDER = Path("data/real/deep")

print("\n===================================")
print("OCEANEMBED DEEP GLORYS INSPECTION")
print("===================================")

files = list(DATA_FOLDER.glob("*.nc"))

if not files:
    print("\nERROR: No NetCDF file found.")
    print("Check:")
    print(DATA_FOLDER)
    raise SystemExit

print("\nFiles found:")

for file in files:
    print("-", file)

input_file = files[0]

print("\nOpening:")
print(input_file)

ds = xr.open_dataset(input_file)

print("\n===================================")
print("DATASET INFORMATION")
print("===================================")

print("\nDimensions:")
print(ds.dims)

print("\nCoordinates:")
print(list(ds.coords))

print("\nVariables:")
print(list(ds.data_vars))

if "depth" in ds.coords:
    print("\nDepth levels:")
    print(ds["depth"].values)

if "latitude" in ds.coords:
    print("\nLatitude range:")
    print(
        float(ds["latitude"].min()),
        "to",
        float(ds["latitude"].max())
    )

if "longitude" in ds.coords:
    print("\nLongitude range:")
    print(
        float(ds["longitude"].min()),
        "to",
        float(ds["longitude"].max())
    )

if "thetao" in ds.data_vars:
    print("\nTemperature statistics:")

    print(
        ds["thetao"].to_dataframe()
        ["thetao"]
        .describe()
    )

print("\n===================================")
print("INSPECTION COMPLETE")
print("===================================")