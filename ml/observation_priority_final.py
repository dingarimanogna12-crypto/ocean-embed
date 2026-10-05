from pathlib import Path
import pandas as pd
import numpy as np

# ============================================================
# STEP 36 — FINAL OBSERVATION PRIORITY ENGINE
# OceanEmbed
# ============================================================

print("\n==============================================")
print("STEP 36 — OBSERVATION PRIORITY ENGINE")
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

UNCERTAINTY_FILE = (
    VALIDATION_DIR
    / "final_uncertainty_profile.csv"
)

OUTPUT_FILE = (
    VALIDATION_DIR
    / "observation_priority_profile.csv"
)


# ============================================================
# STEP 36A — LOAD UNCERTAINTY PROFILE
# ============================================================

print("\nLoading Step-35 uncertainty profile...")

if not UNCERTAINTY_FILE.exists():

    print(
        "\nERROR: Step-35 uncertainty file not found:"
    )

    print(UNCERTAINTY_FILE)

    print(
        "\nPlease complete Step 35 first."
    )

    raise SystemExit(1)


data = pd.read_csv(
    UNCERTAINTY_FILE
)

print(
    "Depth groups loaded:",
    len(data)
)


# ============================================================
# STEP 36B — CALCULATE OBSERVATION PRIORITY
# ============================================================

print(
    "\nCalculating observation priority..."
)


def calculate_priority(row):

    uncertainty = row[
        "uncertainty_90_c"
    ]

    mae = row[
        "mae_c"
    ]

    observations = row[
        "observations"
    ]

    reliability = row[
        "reliability"
    ]

    # --------------------------------------------------------
    # Base uncertainty score
    #
    # 0°C uncertainty  -> 0
    # 3°C uncertainty  -> 100
    # --------------------------------------------------------

    uncertainty_score = min(
        100,
        (uncertainty / 3.0) * 100
    )

    # --------------------------------------------------------
    # Error score
    #
    # 0°C MAE -> 0
    # 3°C MAE -> 100
    # --------------------------------------------------------

    error_score = min(
        100,
        (mae / 3.0) * 100
    )

    # --------------------------------------------------------
    # Low-sample bonus
    #
    # Areas with very few validation observations need
    # additional observations even if current uncertainty
    # looks small.
    # --------------------------------------------------------

    if observations <= 2:

        sample_bonus = 20

    elif observations <= 4:

        sample_bonus = 10

    else:

        sample_bonus = 0


    # --------------------------------------------------------
    # Reliability bonus
    # --------------------------------------------------------

    if reliability == "LOW_SAMPLE":

        reliability_bonus = 15

    elif reliability == "LIMITED_SAMPLE":

        reliability_bonus = 5

    else:

        reliability_bonus = 0


    # --------------------------------------------------------
    # Final priority score
    #
    # Uncertainty is the most important factor.
    # --------------------------------------------------------

    priority_score = (
        0.60 * uncertainty_score
        +
        0.25 * error_score
        +
        0.15 * (
            sample_bonus
            +
            reliability_bonus
        )
    )

    priority_score = min(
        100,
        priority_score
    )


    # --------------------------------------------------------
    # Priority classification
    # --------------------------------------------------------

    if priority_score >= 70:

        priority = "HIGH"

    elif priority_score >= 40:

        priority = "MEDIUM"

    else:

        priority = "LOW"


    # --------------------------------------------------------
    # Observation recommendation
    # --------------------------------------------------------

    if priority == "HIGH":

        recommendation = (
            "Strongly recommend additional "
            "ARGO/in-situ observations"
        )

    elif priority == "MEDIUM":

        recommendation = (
            "Additional observations recommended "
            "for improved confidence"
        )

    else:

        recommendation = (
            "Routine monitoring sufficient"
        )


    return pd.Series({

        "uncertainty_score":
            uncertainty_score,

        "error_score":
            error_score,

        "sample_bonus":
            sample_bonus,

        "reliability_bonus":
            reliability_bonus,

        "priority_score":
            priority_score,

        "observation_priority":
            priority,

        "recommendation":
            recommendation
    })


# ============================================================
# STEP 36C — APPLY PRIORITY ENGINE
# ============================================================

priority_values = data.apply(
    calculate_priority,
    axis=1
)


final_data = pd.concat(
    [
        data,
        priority_values
    ],
    axis=1
)


# ============================================================
# STEP 36D — SORT BY PRIORITY
# ============================================================

final_data = final_data.sort_values(
    by="priority_score",
    ascending=False
).reset_index(
    drop=True
)


# ============================================================
# STEP 36E — PRINT RESULTS
# ============================================================

print(
    "\n=============================================="
)

print(
    "OBSERVATION PRIORITY RESULTS"
)

print(
    "=============================================="
)


display_columns = [
    "depth_bin_m",
    "observations",
    "mae_c",
    "uncertainty_90_c",
    "confidence",
    "reliability",
    "priority_score",
    "observation_priority"
]


print(
    final_data[
        display_columns
    ].to_string(
        index=False
    )
)


# ============================================================
# STEP 36F — PRIORITY SUMMARY
# ============================================================

print(
    "\n=============================================="
)

print(
    "PRIORITY SUMMARY"
)

print(
    "=============================================="
)


priority_counts = (
    final_data[
        "observation_priority"
    ]
    .value_counts()
)


for priority in [
    "HIGH",
    "MEDIUM",
    "LOW"
]:

    count = priority_counts.get(
        priority,
        0
    )

    print(
        f"{priority:8s}: {count}"
    )


# ============================================================
# STEP 36G — TOP PRIORITY DEPTHS
# ============================================================

print(
    "\nTop priority depths:"
)


top_priority = final_data.head(
    10
)


for _, row in top_priority.iterrows():

    print(
        f"Depth {row['depth_bin_m']:.0f} m"
        f" | Score {row['priority_score']:.1f}"
        f" | {row['observation_priority']}"
        f" | Uncertainty ±"
        f"{row['uncertainty_90_c']:.2f}°C"
    )


# ============================================================
# STEP 36H — SAVE
# ============================================================

final_data.to_csv(
    OUTPUT_FILE,
    index=False
)


print(
    "\nSaved observation priority profile:"
)

print(
    OUTPUT_FILE
)


# ============================================================
# STEP 36 COMPLETE
# ============================================================

print(
    "\n=============================================="
)

print(
    "STEP 36 COMPLETE"
)

print(
    "=============================================="
)

print(
    "\nOceanEmbed can now identify depths where"
)

print(
    "additional observations are most valuable."
)

print(
    "\nThis creates the closed-loop concept:"
)

print(
    "Prediction"
    " → Uncertainty"
    " → Observation Priority"
    " → Additional Data"
    " → Improved Model"
)