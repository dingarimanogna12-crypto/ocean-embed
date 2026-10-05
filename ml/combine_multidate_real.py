import xarray as xr
import pandas as pd
from pathlib import Path

# ==========================================
# OCEANEMBED MULTI-DATE REAL DATA COMBINATION
# ==========================================

BASE_DIR = Path("data/real/multidate")

THETA_DIR = BASE_DIR / "thetao"
SURFACE_DIR = BASE_DIR / "surface"

OUTPUT_FILE = Path("data/real/multidate_real_training.csv")

DATES = [
    "2020-01-01",
    "2020-02-01",
    "2020-03-01",
    "2020-04-01",
    "2020-05-01",
    "2020-06-01",
    "2020-07-01",
    "2020-08-01",
    "2020-09-01",
    "2020-10-01",
]

print("\n===================================")
print("OCEANEMBED MULTI-DATE DATA")
print("COMBINATION")
print("===================================")

all_data = []

for date in DATES:

    print("\n-----------------------------------")
    print("Processing:", date)
    print("-----------------------------------")

    # -----------------------------------
    # Find files
    # -----------------------------------

    theta_files = list(
        THETA_DIR.glob(f"*thetao*{date}.nc")
    )

    so_files = list(
        SURFACE_DIR.glob(f"*so*{date}.nc")
    )

    uo_files = list(
        SURFACE_DIR.glob(f"*uo*{date}.nc")
    )

    vo_files = list(
        SURFACE_DIR.glob(f"*vo*{date}.nc")
    )

    zos_files = list(
        SURFACE_DIR.glob(f"*zos*{date}.nc")
    )

    if not theta_files:
        print("ERROR: thetao file not found")
        continue

    if not so_files:
        print("ERROR: so file not found")
        continue

    if not uo_files:
        print("ERROR: uo file not found")
        continue

    if not vo_files:
        print("ERROR: vo file not found")
        continue

    if not zos_files:
        print("ERROR: zos file not found")
        continue

    theta_file = theta_files[0]
    so_file = so_files[0]
    uo_file = uo_files[0]
    vo_file = vo_files[0]
    zos_file = zos_files[0]

    print("thetao:", theta_file.name)
    print("so    :", so_file.name)
    print("uo    :", uo_file.name)
    print("vo    :", vo_file.name)
    print("zos   :", zos_file.name)

    # -----------------------------------
    # Open datasets
    # -----------------------------------

    theta_ds = xr.open_dataset(theta_file)
    so_ds = xr.open_dataset(so_file)
    uo_ds = xr.open_dataset(uo_file)
    vo_ds = xr.open_dataset(vo_file)
    zos_ds = xr.open_dataset(zos_file)

    # -----------------------------------
    # Detect variable names
    # -----------------------------------

    theta = theta_ds["thetao"]
    salinity = so_ds["so"]
    current_u = uo_ds["uo"]
    current_v = vo_ds["vo"]
    ssh = zos_ds["zos"]

    # -----------------------------------
    # Convert temperature to dataframe
    # -----------------------------------

    temperature_df = (
        theta
        .to_dataframe(name="temperature")
        .reset_index()
    )

    temperature_df = temperature_df.dropna(
        subset=["temperature"]
    )

    # -----------------------------------
    # Surface variables
    # -----------------------------------

    # Surface temperature
    sst_df = (
        theta.isel(depth=0)
        .to_dataframe(name="sst")
        .reset_index()
    )

    # Surface salinity
    sss_df = (
        salinity.isel(depth=0)
        .to_dataframe(name="sss")
        .reset_index()
    )

    # Surface eastward current
    uo_df = (
        current_u.isel(depth=0)
        .to_dataframe(name="current_u")
        .reset_index()
    )

    # Surface northward current
    vo_df = (
        current_v.isel(depth=0)
        .to_dataframe(name="current_v")
        .reset_index()
    )

    # Sea surface height
    ssh_df = (
        ssh
        .to_dataframe(name="ssh")
        .reset_index()
    )

    # -----------------------------------
    # Keep only required columns
    # -----------------------------------

    temperature_df = temperature_df[
        [
            "time",
            "latitude",
            "longitude",
            "depth",
            "temperature",
        ]
    ]

    sst_df = sst_df[
        [
            "time",
            "latitude",
            "longitude",
            "sst",
        ]
    ]

    sss_df = sss_df[
        [
            "time",
            "latitude",
            "longitude",
            "sss",
        ]
    ]

    uo_df = uo_df[
        [
            "time",
            "latitude",
            "longitude",
            "current_u",
        ]
    ]

    vo_df = vo_df[
        [
            "time",
            "latitude",
            "longitude",
            "current_v",
        ]
    ]

    ssh_df = ssh_df[
        [
            "time",
            "latitude",
            "longitude",
            "ssh",
        ]
    ]

    # -----------------------------------
    # Merge surface variables
    # -----------------------------------

    surface_df = sst_df.merge(
        sss_df,
        on=["time", "latitude", "longitude"],
        how="inner",
    )

    surface_df = surface_df.merge(
        uo_df,
        on=["time", "latitude", "longitude"],
        how="inner",
    )

    surface_df = surface_df.merge(
        vo_df,
        on=["time", "latitude", "longitude"],
        how="inner",
    )

    surface_df = surface_df.merge(
        ssh_df,
        on=["time", "latitude", "longitude"],
        how="inner",
    )

    print(
        "Surface records:",
        len(surface_df)
    )

    # -----------------------------------
    # Merge surface + temperature
    # -----------------------------------

    combined_df = temperature_df.merge(
        surface_df,
        on=[
            "time",
            "latitude",
            "longitude",
        ],
        how="inner",
    )

    # -----------------------------------
    # Add date
    # -----------------------------------

    combined_df["date"] = pd.to_datetime(
        combined_df["time"]
    ).dt.strftime("%Y-%m-%d")

    # -----------------------------------
    # Reorder columns
    # -----------------------------------

    combined_df = combined_df[
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
            "temperature",
        ]
    ]

    combined_df = combined_df.dropna()

    print(
        "Combined records:",
        len(combined_df)
    )

    print(
        "Depth levels:",
        combined_df["depth"].nunique()
    )

    all_data.append(combined_df)

    # -----------------------------------
    # Close datasets
    # -----------------------------------

    theta_ds.close()
    so_ds.close()
    uo_ds.close()
    vo_ds.close()
    zos_ds.close()


# ==========================================
# COMBINE ALL DATES
# ==========================================

if not all_data:
    raise RuntimeError(
        "No data was successfully combined."
    )

final_df = pd.concat(
    all_data,
    ignore_index=True
)

# ==========================================
# Sort
# ==========================================

final_df = final_df.sort_values(
    [
        "date",
        "latitude",
        "longitude",
        "depth",
    ]
)

# ==========================================
# Save
# ==========================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

final_df.to_csv(
    OUTPUT_FILE,
    index=False
)

# ==========================================
# FINAL SUMMARY
# ==========================================

print("\n===================================")
print("MULTI-DATE COMBINATION COMPLETE")
print("===================================")

print(
    "\nTotal records:",
    len(final_df)
)

print(
    "\nDates:",
    final_df["date"].nunique()
)

print(
    "\nDepth levels:",
    final_df["depth"].nunique()
)

print(
    "\nDepth range:",
    final_df["depth"].min(),
    "to",
    final_df["depth"].max(),
    "m"
)

print(
    "\nLatitude range:",
    final_df["latitude"].min(),
    "to",
    final_df["latitude"].max()
)

print(
    "\nLongitude range:",
    final_df["longitude"].min(),
    "to",
    final_df["longitude"].max()
)

print("\nColumns:")
print(list(final_df.columns))

print("\nRecords per date:")
print(
    final_df.groupby("date").size()
)

print("\nFirst 10 records:")
print(
    final_df.head(10)
)

print("\nTemperature statistics:")
print(
    final_df["temperature"].describe()
)

print("\nSaved successfully to:")
print(OUTPUT_FILE)