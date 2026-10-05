from pathlib import Path
import subprocess


# ==================================================
# SETTINGS
# ==================================================

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

DATASET = "cmems_mod_glo_phy_my_0.083deg_P1D-m"

MIN_LON = "70"
MAX_LON = "75"

MIN_LAT = "10"
MAX_LAT = "15"

MIN_DEPTH = "0.49"
MAX_DEPTH = "902"

BASE_DIR = Path("data/real/multidate")

THETA_DIR = BASE_DIR / "thetao"
SURFACE_DIR = BASE_DIR / "surface"


# ==================================================
# CREATE DIRECTORIES
# ==================================================

THETA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

SURFACE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==================================================
# VARIABLES
# ==================================================

VARIABLES = [
    "thetao",
    "so",
    "uo",
    "vo",
    "zos"
]


# ==================================================
# DOWNLOAD FUNCTION
# ==================================================

def download_variable(
    variable,
    date
):

    if variable == "thetao":

        output_dir = THETA_DIR

        minimum_depth = MIN_DEPTH
        maximum_depth = MAX_DEPTH

    elif variable in [
        "so",
        "uo",
        "vo"
    ]:

        output_dir = SURFACE_DIR

        minimum_depth = "0.49"
        maximum_depth = "0.50"

    else:

        output_dir = SURFACE_DIR

        minimum_depth = None
        maximum_depth = None


    print("\n-----------------------------------")
    print(
        f"Variable: {variable}"
    )
    print(
        f"Date: {date}"
    )
    print("-----------------------------------")


    # --------------------------------------------------
    # CHECK IF FILE ALREADY EXISTS
    # --------------------------------------------------

    existing_files = list(
        output_dir.glob(
            f"*_{variable}_*_{date}.nc"
        )
    )

    if existing_files:

        print(
            "Already downloaded:"
        )

        for file in existing_files:
            print(file)

        return True


    # --------------------------------------------------
    # BUILD COMMAND
    # --------------------------------------------------

    command = [
        "copernicusmarine",
        "subset",

        "--dataset-id",
        DATASET,

        "--variable",
        variable,

        "--start-datetime",
        f"{date}T00:00:00",

        "--end-datetime",
        f"{date}T00:00:00",

        "--minimum-longitude",
        MIN_LON,

        "--maximum-longitude",
        MAX_LON,

        "--minimum-latitude",
        MIN_LAT,

        "--maximum-latitude",
        MAX_LAT,

        "--output-directory",
        str(output_dir)
    ]


    # --------------------------------------------------
    # ADD DEPTH FOR 3D VARIABLES
    # --------------------------------------------------

    if variable != "zos":

        command.extend([
            "--minimum-depth",
            minimum_depth,

            "--maximum-depth",
            maximum_depth
        ])


    # --------------------------------------------------
    # RUN DOWNLOAD
    # --------------------------------------------------

    print(
        "\nStarting download..."
    )

    result = subprocess.run(
        command
    )


    # --------------------------------------------------
    # RESULT
    # --------------------------------------------------

    if result.returncode == 0:

        print(
            f"\nSUCCESS: {variable} "
            f"{date}"
        )

        return True

    else:

        print(
            f"\nFAILED: {variable} "
            f"{date}"
        )

        return False


# ==================================================
# MAIN DOWNLOAD LOOP
# ==================================================

print("\n===================================")
print("OCEANEMBED MULTI-DATE GLORYS")
print("DOWNLOAD")
print("===================================")

print("\nDates:")
for date in DATES:
    print(" -", date)

print("\nVariables:")
for variable in VARIABLES:
    print(" -", variable)

print("\nRegion:")
print("Latitude :", MIN_LAT, "to", MAX_LAT)
print("Longitude:", MIN_LON, "to", MAX_LON)


successful = 0
failed = 0


# ==================================================
# DOWNLOAD EVERYTHING
# ==================================================

for date in DATES:

    for variable in VARIABLES:

        success = download_variable(
            variable,
            date
        )

        if success:
            successful += 1
        else:
            failed += 1


# ==================================================
# FINAL SUMMARY
# ==================================================

print("\n===================================")
print("DOWNLOAD SUMMARY")
print("===================================")

print(
    "\nSuccessful:",
    successful
)

print(
    "Failed:",
    failed
)

print(
    "\nTheta files:"
)

for file in sorted(
    THETA_DIR.glob("*.nc")
):

    print(
        " ",
        file.name
    )


print(
    "\nSurface files:"
)

for file in sorted(
    SURFACE_DIR.glob("*.nc")
):

    print(
        " ",
        file.name
    )


print("\n===================================")
print("STEP 31A COMPLETE")
print("===================================")