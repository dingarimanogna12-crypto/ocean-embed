import xarray as xr
import pandas as pd
from pathlib import Path

print("\n===================================")
print("OCEANEMBED REAL GLORYS DATA")
print("===================================")


# --------------------------------------------------
# FILES
# --------------------------------------------------

THETA_FILE = (
    "data/real/deep/"
    "cmems_mod_glo_phy_my_0.083deg_P1D-m_thetao_"
    "70.00E-75.00E_10.00N-15.00N_0.49-902.34m_"
    "2020-01-01.nc"
)

SO_FILE = (
    "data/real/surface/"
    "cmems_mod_glo_phy_my_0.083deg_P1D-m_so_"
    "70.00E-75.00E_10.00N-15.00N_0.49m_"
    "2020-01-01.nc"
)

UO_FILE = (
    "data/real/surface/"
    "cmems_mod_glo_phy_my_0.083deg_P1D-m_uo_"
    "70.00E-75.00E_10.00N-15.00N_0.49m_"
    "2020-01-01.nc"
)

VO_FILE = (
    "data/real/surface/"
    "cmems_mod_glo_phy_my_0.083deg_P1D-m_vo_"
    "70.00E-75.00E_10.00N-15.00N_0.49m_"
    "2020-01-01.nc"
)

ZOS_FILE = (
    "data/real/surface/"
    "cmems_mod_glo_phy_my_0.083deg_P1D-m_zos_"
    "70.00E-75.00E_10.00N-15.00N_"
    "2020-01-01.nc"
)

OUTPUT_FILE = "data/real/real_glorys_training.csv"


# --------------------------------------------------
# CHECK FILES
# --------------------------------------------------

print("\nChecking input files...")

files = [
    THETA_FILE,
    SO_FILE,
    UO_FILE,
    VO_FILE,
    ZOS_FILE
]

for file in files:

    if not Path(file).exists():

        raise FileNotFoundError(
            f"\nFile not found:\n{file}"
        )

    print("FOUND:", file)


# --------------------------------------------------
# OPEN DATASETS
# --------------------------------------------------

print("\nOpening GLORYS datasets...")

theta_ds = xr.open_dataset(THETA_FILE)
so_ds = xr.open_dataset(SO_FILE)
uo_ds = xr.open_dataset(UO_FILE)
vo_ds = xr.open_dataset(VO_FILE)
zos_ds = xr.open_dataset(ZOS_FILE)

print("All datasets opened successfully!")


# --------------------------------------------------
# EXTRACT VARIABLES
# --------------------------------------------------

theta = theta_ds["thetao"]
salinity = so_ds["so"]
current_u = uo_ds["uo"]
current_v = vo_ds["vo"]
ssh = zos_ds["zos"]


# --------------------------------------------------
# SURFACE SALINITY
# --------------------------------------------------

print("\nReading salinity...")

surface_so = (
    salinity
    .to_dataframe(name="sss")
    .reset_index()
)

surface_so = surface_so[
    [
        "time",
        "latitude",
        "longitude",
        "sss"
    ]
]


# --------------------------------------------------
# SURFACE CURRENT U
# --------------------------------------------------

print("Reading eastward current...")

surface_uo = (
    current_u
    .to_dataframe(name="current_u")
    .reset_index()
)

surface_uo = surface_uo[
    [
        "time",
        "latitude",
        "longitude",
        "current_u"
    ]
]


# --------------------------------------------------
# SURFACE CURRENT V
# --------------------------------------------------

print("Reading northward current...")

surface_vo = (
    current_v
    .to_dataframe(name="current_v")
    .reset_index()
)

surface_vo = surface_vo[
    [
        "time",
        "latitude",
        "longitude",
        "current_v"
    ]
]


# --------------------------------------------------
# SEA SURFACE HEIGHT
# --------------------------------------------------

print("Reading sea-surface height...")

surface_zos = (
    ssh
    .to_dataframe(name="ssh")
    .reset_index()
)

surface_zos = surface_zos[
    [
        "time",
        "latitude",
        "longitude",
        "ssh"
    ]
]


# --------------------------------------------------
# SST
# --------------------------------------------------
# The first GLORYS thetao level is approximately
# 0.494 m and is used as the surface temperature proxy.

print("Reading surface temperature...")

surface_theta = (
    theta
    .isel(depth=0)
    .to_dataframe(name="sst")
    .reset_index()
)

surface_theta = surface_theta[
    [
        "time",
        "latitude",
        "longitude",
        "sst"
    ]
]


# --------------------------------------------------
# COMBINE SURFACE VARIABLES
# --------------------------------------------------

print("\nCombining surface variables...")

surface = surface_theta.merge(
    surface_so,
    on=[
        "time",
        "latitude",
        "longitude"
    ],
    how="inner"
)

surface = surface.merge(
    surface_uo,
    on=[
        "time",
        "latitude",
        "longitude"
    ],
    how="inner"
)

surface = surface.merge(
    surface_vo,
    on=[
        "time",
        "latitude",
        "longitude"
    ],
    how="inner"
)

surface = surface.merge(
    surface_zos,
    on=[
        "time",
        "latitude",
        "longitude"
    ],
    how="inner"
)


# --------------------------------------------------
# REMOVE DUPLICATES
# --------------------------------------------------

surface = surface.drop_duplicates(
    subset=[
        "time",
        "latitude",
        "longitude"
    ]
)


print(
    "\nSurface records:",
    len(surface)
)

print("\nSurface columns:")
print(list(surface.columns))


# --------------------------------------------------
# SUBSURFACE TEMPERATURE
# --------------------------------------------------

print("\nPreparing subsurface temperature...")

temperature = (
    theta
    .to_dataframe(name="temperature")
    .reset_index()
)

temperature = temperature.dropna(
    subset=["temperature"]
)


# IMPORTANT:
# temperature keeps its depth column.
# surface does NOT contain depth.


print(
    "\nTemperature records:",
    len(temperature)
)


# --------------------------------------------------
# MERGE SURFACE + SUBSURFACE
# --------------------------------------------------

print("\nCombining surface and subsurface data...")

training = temperature.merge(
    surface,
    on=[
        "time",
        "latitude",
        "longitude"
    ],
    how="inner"
)


# --------------------------------------------------
# DATE
# --------------------------------------------------

training["date"] = pd.to_datetime(
    training["time"]
).dt.date


# --------------------------------------------------
# FINAL COLUMNS
# --------------------------------------------------

training = training[
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
        "temperature"
    ]
]


# --------------------------------------------------
# REMOVE MISSING VALUES
# --------------------------------------------------

training = training.dropna()


# --------------------------------------------------
# SORT
# --------------------------------------------------

training = training.sort_values(
    [
        "date",
        "latitude",
        "longitude",
        "depth"
    ]
)


# --------------------------------------------------
# SAVE
# --------------------------------------------------

Path("data/real").mkdir(
    parents=True,
    exist_ok=True
)

training.to_csv(
    OUTPUT_FILE,
    index=False
)


# --------------------------------------------------
# RESULTS
# --------------------------------------------------

print("\n===================================")
print("REAL GLORYS DATASET CREATED")
print("===================================")

print("\nTotal records:")
print(len(training))

print("\nColumns:")
print(list(training.columns))

print("\nNumber of depth levels:")
print(
    training["depth"].nunique()
)

print("\nDepth range:")
print(
    training["depth"].min(),
    "to",
    training["depth"].max(),
    "m"
)

print("\nLatitude range:")
print(
    training["latitude"].min(),
    "to",
    training["latitude"].max()
)

print("\nLongitude range:")
print(
    training["longitude"].min(),
    "to",
    training["longitude"].max()
)

print("\nTemperature statistics:")
print(
    training["temperature"].describe()
)

print("\nFirst 10 records:")
print(
    training.head(10)
)

print("\nSaved to:")
print(OUTPUT_FILE)

print("\n===================================")
print("STEP 30C COMPLETE")
print("===================================")