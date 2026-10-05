import xarray as xr

file_path = "ml/data/real/test_glorys.nc"

ds = xr.open_dataset(file_path)

print("\nOcean dataset:")
print(ds)

print("\nVariables:")
print(list(ds.data_vars))

print("\nCoordinates:")
print(list(ds.coords))