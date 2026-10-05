import sys
import json
import warnings
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

warnings.filterwarnings(
    "ignore",
    message="X does not have valid feature names.*",
    category=UserWarning,
)

OUTPUT_PATH = sys.argv[2] if len(sys.argv) > 2 else None


# ============================================================
# OCEANEMBED STEP-32 WEB PREDICTION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "oceanembed_step32_neural.pkl"
)

UNCERTAINTY_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "validation"
    / "final_uncertainty_profile.csv"
)

PRIORITY_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "validation"
    / "observation_priority_profile.csv"
)


# Standard depths available in the current real GLORYS dataset.
STANDARD_DEPTHS = [
    0,
    5,
    10,
    20,
    30,
    50,
    75,
    100,
    125,
    150,
    200,
    300,
    500,
    700
]


def main():

    # --------------------------------------------------------
    # 1. Load JSON input
    # --------------------------------------------------------

    try:
        raw_input = sys.stdin.read()

        if not raw_input.strip():
            raise ValueError("No input received.")

        data = json.loads(raw_input)

    except Exception as e:

        print(json.dumps({
            "success": False,
            "error": f"Invalid input: {str(e)}"
        }))

        return


    # --------------------------------------------------------
    # 2. Validate input
    # --------------------------------------------------------

    required_fields = [
        "latitude",
        "longitude",
        "sst",
        "sss",
        "ssh",
        "current_u",
        "current_v"
    ]

    missing = [
        field
        for field in required_fields
        if field not in data
    ]

    if missing:

        print(json.dumps({
            "success": False,
            "error": "Missing fields: " + ", ".join(missing)
        }))

        return


    # --------------------------------------------------------
    # 3. Load Step-32 model
    # --------------------------------------------------------

    try:

        bundle = joblib.load(MODEL_PATH)

        if not isinstance(bundle, dict):

            raise ValueError(
                "Step-32 model file does not contain the expected dictionary."
            )

        model = bundle["model"]
        x_scaler = bundle["x_scaler"]
        y_scaler = bundle["y_scaler"]

        features = bundle.get(
            "features",
            [
                "sst",
                "sss",
                "ssh",
                "current_u",
                "current_v",
                "depth"
            ]
        )

    except Exception as e:

        print(json.dumps({
            "success": False,
            "error": f"Could not load Step-32 model: {str(e)}"
        }))

        return


    # --------------------------------------------------------
    # 4. Create prediction rows
    # --------------------------------------------------------

    rows = []

    for depth in STANDARD_DEPTHS:

        rows.append({
            "sst": float(data["sst"]),
            "sss": float(data["sss"]),
            "ssh": float(data["ssh"]),
            "current_u": float(data["current_u"]),
            "current_v": float(data["current_v"]),
            "depth": float(depth)
        })


    df = pd.DataFrame(rows)

    # Make sure feature order exactly matches training.
    df = df[features]


    # --------------------------------------------------------
    # 5. Scale inputs
    # --------------------------------------------------------

    X_scaled = x_scaler.transform(df)


    # --------------------------------------------------------
    # 6. Predict temperature
    # --------------------------------------------------------

    y_scaled = model.predict(X_scaled)

    y_scaled = np.asarray(y_scaled).reshape(-1, 1)

    temperatures = y_scaler.inverse_transform(
        y_scaled
    ).flatten()


    # --------------------------------------------------------
    # 7. Load validation uncertainty and priority data
    # --------------------------------------------------------

    try:

        uncertainty_df = pd.read_csv(UNCERTAINTY_PATH)
        priority_df = pd.read_csv(PRIORITY_PATH)

    except Exception as e:

        print(json.dumps({
            "success": False,
            "error": f"Could not load validation data: {str(e)}"
        }))

        return


    # --------------------------------------------------------
    # 8. Build temperature + validation profile
    # --------------------------------------------------------

    profile = []

    for depth, temperature in zip(
        STANDARD_DEPTHS,
        temperatures
    ):

        depth_value = float(depth)

        # Find the uncertainty bin containing this depth.
        uncertainty_match = uncertainty_df[
            (uncertainty_df["depth_min_m"] <= depth_value) &
            (depth_value < uncertainty_df["depth_max_m"])
        ]

        uncertainty = None
        confidence = None
        priority = None

        if not uncertainty_match.empty:

            row = uncertainty_match.iloc[0]

            uncertainty = round(
                float(row["uncertainty_90_c"]),
                3
            )

            confidence = str(
                row["confidence"]
            )


            # Match the same depth bin in the priority table.
            priority_match = priority_df[
                (priority_df["depth_min_m"] <= depth_value) &
                (depth_value < priority_df["depth_max_m"])
            ]

            if not priority_match.empty:

                priority = str(
                    priority_match.iloc[0]["observation_priority"]
                )


        profile.append({
            "depth": depth,
            "temperature": round(float(temperature), 3),
            "uncertainty": uncertainty,
            "confidence": confidence,
            "priority": priority
        })


    # --------------------------------------------------------
    # 9. Return result
    # --------------------------------------------------------

    result = {

        "success": True,

        "model": "OceanEmbed Step-32 Neural Network",

        "latitude": float(data["latitude"]),

        "longitude": float(data["longitude"]),

        "profile": profile,

        "notes": [
            "Predictions generated using the Step-32 neural network.",
            "Current real GLORYS training data extends to approximately 763 m.",
            "The web profile therefore uses standard depths up to 700 m.",
            "This is a research prototype and not an operational ocean product."
        ]

    }


    if OUTPUT_PATH:
        Path(OUTPUT_PATH).write_text(
            json.dumps(result, indent=2),
            encoding="utf-8"
        )

    print(
        json.dumps(
            result,
            indent=2
        )
    )


if __name__ == "__main__":
    main()