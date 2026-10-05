from pathlib import Path
import numpy as np
import pandas as pd

# ============================================================
# STEP 35 — FINAL UNCERTAINTY / CONFIDENCE
# OceanEmbed
# ============================================================

print("\n==============================================")
print("STEP 35 — FINAL UNCERTAINTY / CONFIDENCE")
print("==============================================")

# ------------------------------------------------------------
# 1. PATHS
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

VALIDATION_DIR = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "validation"
)

VALIDATION_FILE = (
    VALIDATION_DIR
    / "argo_validation_results.csv"
)

DEPTH_FILE = (
    VALIDATION_DIR
    / "argo_depth_results.csv"
)

OUTPUT_FILE = (
    VALIDATION_DIR
    / "final_uncertainty_profile.csv"
)

SUMMARY_FILE = (
    VALIDATION_DIR
    / "final_uncertainty_summary.csv"
)


# ============================================================
# STEP 35A — LOAD ARGO VALIDATION
# ============================================================

print("\nLoading real ARGO validation results...")

if not VALIDATION_FILE.exists():

    print(
        "\nERROR: ARGO validation results not found:"
    )

    print(VALIDATION_FILE)

    print(
        "\nPlease complete Step 34 first."
    )

    raise SystemExit(1)


data = pd.read_csv(
    VALIDATION_FILE
)

print(
    "Validation observations:",
    len(data)
)


# ============================================================
# STEP 35B — CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "argo_depth",
    "argo_temperature",
    "oceanembed_temperature",
    "error",
    "absolute_error"
]

missing = [
    column
    for column in required_columns
    if column not in data.columns
]

if missing:

    print(
        "\nERROR: Missing columns:"
    )

    for column in missing:
        print(
            " -",
            column
        )

    raise SystemExit(1)


# ============================================================
# STEP 35C — CREATE DEPTH BINS
# ============================================================

print(
    "\nCreating depth-wise uncertainty groups..."
)

# 25 m depth bins
data["depth_bin"] = (
    np.floor(
        data["argo_depth"] / 25
    )
    * 25
)


# ============================================================
# STEP 35D — CALCULATE DEPTH-WISE UNCERTAINTY
# ============================================================

results = []


for depth_bin, group in data.groupby(
    "depth_bin"
):

    errors = (
        group["error"]
        .to_numpy()
    )

    absolute_errors = (
        group["absolute_error"]
        .to_numpy()
    )

    n = len(group)

    # --------------------------------------------------------
    # Mean error
    # --------------------------------------------------------

    mean_error = np.mean(
        errors
    )

    # --------------------------------------------------------
    # MAE
    # --------------------------------------------------------

    mae = np.mean(
        absolute_errors
    )

    # --------------------------------------------------------
    # Error standard deviation
    # --------------------------------------------------------

    if n > 1:

        error_std = np.std(
            errors,
            ddof=1
        )

    else:

        error_std = 0.0

    # --------------------------------------------------------
    # Absolute-error 90th percentile
    # --------------------------------------------------------

    p90_abs_error = np.percentile(
        absolute_errors,
        90
    )

    # --------------------------------------------------------
    # Approximate 90% prediction interval
    #
    # Uses:
    # mean error ± 1.645 × standard deviation
    # --------------------------------------------------------

    lower_error = (
        mean_error
        -
        1.645 * error_std
    )

    upper_error = (
        mean_error
        +
        1.645 * error_std
    )

    # --------------------------------------------------------
    # Convert to temperature uncertainty
    # --------------------------------------------------------

    uncertainty = (
        1.645 * error_std
    )

    # --------------------------------------------------------
    # Confidence classification
    #
    # HIGH:
    # uncertainty < 0.5°C
    #
    # MEDIUM:
    # uncertainty < 1.0°C
    #
    # LOW:
    # uncertainty >= 1.0°C
    # --------------------------------------------------------

    if uncertainty < 0.5:

        confidence = "HIGH"

    elif uncertainty < 1.0:

        confidence = "MEDIUM"

    else:

        confidence = "LOW"


    # --------------------------------------------------------
    # Reliability warning
    # --------------------------------------------------------

    if n < 3:

        reliability = "LOW_SAMPLE"

    elif n < 5:

        reliability = "LIMITED_SAMPLE"

    else:

        reliability = "SUPPORTED"


    results.append({

        "depth_bin_m": depth_bin,

        "depth_min_m": depth_bin,

        "depth_max_m": depth_bin + 25,

        "observations": n,

        "mean_error_c": mean_error,

        "mae_c": mae,

        "error_std_c": error_std,

        "p90_absolute_error_c":
            p90_abs_error,

        "uncertainty_90_c":
            uncertainty,

        "lower_error_90_c":
            lower_error,

        "upper_error_90_c":
            upper_error,

        "confidence":
            confidence,

        "reliability":
            reliability

    })


uncertainty_profile = pd.DataFrame(
    results
)


# ============================================================
# STEP 35E — OVERALL UNCERTAINTY
# ============================================================

all_errors = (
    data["error"]
    .to_numpy()
)

all_absolute_errors = (
    data["absolute_error"]
    .to_numpy()
)


overall_mae = np.mean(
    all_absolute_errors
)

overall_bias = np.mean(
    all_errors
)

overall_std = np.std(
    all_errors,
    ddof=1
)

overall_uncertainty = (
    1.645 * overall_std
)

overall_p90 = np.percentile(
    all_absolute_errors,
    90
)


if overall_uncertainty < 0.5:

    overall_confidence = "HIGH"

elif overall_uncertainty < 1.0:

    overall_confidence = "MEDIUM"

else:

    overall_confidence = "LOW"


# ============================================================
# STEP 35F — SUMMARY
# ============================================================

summary = pd.DataFrame([
    {
        "validation_observations":
            len(data),

        "overall_mae_c":
            overall_mae,

        "overall_bias_c":
            overall_bias,

        "error_std_c":
            overall_std,

        "uncertainty_90_c":
            overall_uncertainty,

        "p90_absolute_error_c":
            overall_p90,

        "overall_confidence":
            overall_confidence,

        "validation_region":
            "10-15N, 70-75E",

        "validation_period":
            "2020-01 to 2020-10",

        "validation_reference":
            "Real ARGO"
    }
])


# ============================================================
# STEP 35G — PRINT RESULTS
# ============================================================

print("\n==============================================")
print("STEP 35 — UNCERTAINTY RESULTS")
print("==============================================")


print(
    f"\nValidation observations : "
    f"{len(data):,}"
)

print(
    f"Overall MAE            : "
    f"{overall_mae:.3f} °C"
)

print(
    f"Overall Bias           : "
    f"{overall_bias:.3f} °C"
)

print(
    f"Error Std              : "
    f"{overall_std:.3f} °C"
)

print(
    f"90% Uncertainty       : "
    f"±{overall_uncertainty:.3f} °C"
)

print(
    f"90th Percentile Error : "
    f"{overall_p90:.3f} °C"
)

print(
    f"Overall Confidence    : "
    f"{overall_confidence}"
)


# ============================================================
# STEP 35H — DEPTH-WISE RESULTS
# ============================================================

print(
    "\nDepth-wise uncertainty:"
)

print(
    uncertainty_profile[
        [
            "depth_bin_m",
            "observations",
            "mae_c",
            "error_std_c",
            "uncertainty_90_c",
            "confidence",
            "reliability"
        ]
    ].to_string(
        index=False
    )
)


# ============================================================
# STEP 35I — SAVE FILES
# ============================================================

uncertainty_profile.to_csv(
    OUTPUT_FILE,
    index=False
)

summary.to_csv(
    SUMMARY_FILE,
    index=False
)


print(
    "\nSaved uncertainty profile:"
)

print(
    OUTPUT_FILE
)


print(
    "\nSaved uncertainty summary:"
)

print(
    SUMMARY_FILE
)


# ============================================================
# STEP 35 COMPLETE
# ============================================================

print("\n==============================================")
print("STEP 35 COMPLETE")
print("==============================================")

print(
    "\nFinal uncertainty system is based on "
    "real ARGO validation residuals."
)

print(
    "\nImportant:"
)

print(
    "Confidence represents validation-based "
    "model reliability, not a guaranteed physical "
    "probability interval."
)