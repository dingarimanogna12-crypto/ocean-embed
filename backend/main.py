from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

app = FastAPI(title="OceanEmbed Prediction API")

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "model"

MODEL_PATH = MODEL_DIR / "oceanembed_step32_neural.pkl"
UNCERTAINTY_PATH = MODEL_DIR / "final_uncertainity_profile.csv"
PRIORITY_PATH = MODEL_DIR / "observation_priority_profile.csv"

STANDARD_DEPTHS = [
    0, 5, 10, 20, 30, 50, 75,
    100, 125, 150, 200, 300, 500, 700
]

bundle = joblib.load(MODEL_PATH)
model = bundle["model"]
x_scaler = bundle["x_scaler"]
y_scaler = bundle["y_scaler"]

features = bundle.get(
    "features",
    ["sst", "sss", "ssh", "current_u", "current_v", "depth"]
)

uncertainty_df = pd.read_csv(UNCERTAINTY_PATH)
priority_df = pd.read_csv(PRIORITY_PATH)


class PredictionInput(BaseModel):
    latitude: float
    longitude: float
    sst: float
    sss: float
    ssh: float
    current_u: float
    current_v: float


@app.get("/")
def root():
    return {
        "success": True,
        "service": "OceanEmbed Prediction API"
    }


@app.post("/predict")
def predict(data: PredictionInput):

    rows = []

    for depth in STANDARD_DEPTHS:
        rows.append({
            "sst": data.sst,
            "sss": data.sss,
            "ssh": data.ssh,
            "current_u": data.current_u,
            "current_v": data.current_v,
            "depth": float(depth)
        })

    df = pd.DataFrame(rows)
    df = df[features]

    X_scaled = x_scaler.transform(df)

    y_scaled = model.predict(X_scaled)

    y_scaled = np.asarray(y_scaled).reshape(-1, 1)

    temperatures = y_scaler.inverse_transform(
        y_scaled
    ).flatten()

    profile = []

    for depth, temperature in zip(
        STANDARD_DEPTHS,
        temperatures
    ):

        uncertainty_match = uncertainty_df[
            (uncertainty_df["depth_min_m"] <= depth)
            & (depth < uncertainty_df["depth_max_m"])
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

            confidence = str(row["confidence"])

            priority_match = priority_df[
                (priority_df["depth_min_m"] <= depth)
                & (depth < priority_df["depth_max_m"])
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

    return {
        "success": True,
        "model": "OceanEmbed Step-32 Neural Network",
        "latitude": data.latitude,
        "longitude": data.longitude,
        "profile": profile,
        "notes": [
            "Predictions generated using the Step-32 neural network.",
            "Current real GLORYS training data extends to approximately 763 m.",
            "The web profile therefore uses standard depths up to 700 m.",
            "This is a research prototype and not an operational ocean product."
        ]
    }
