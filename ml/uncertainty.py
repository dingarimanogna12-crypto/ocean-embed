import sys
import json
import warnings
from pathlib import Path
import joblib
import numpy as np

warnings.filterwarnings(
    "ignore",
    message="X does not have valid feature names.*",
    category=UserWarning,
)

MODEL_FILE = "ml/models/oceanembed_multidepth_model.pkl"
OUTPUT_PATH = sys.argv[2] if len(sys.argv) > 2 else None

DEPTHS = [
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
    700,
    1000
]


def write_result(payload):
    if OUTPUT_PATH:
        Path(OUTPUT_PATH).write_text(json.dumps(payload), encoding="utf-8")
    print(json.dumps(payload))


try:
    raw_input = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()

    if not raw_input or not raw_input.strip():
        raise ValueError("No input data received.")

    input_data = json.loads(raw_input)

    model = joblib.load(MODEL_FILE)

    results = []

    for depth in DEPTHS:
        features = [[
            float(input_data["sst"]),
            float(input_data["sss"]),
            float(input_data["ssh"]),
            float(input_data["current_u"]),
            float(input_data["current_v"]),
            float(input_data["wind_u"]),
            float(input_data["wind_v"]),
            float(depth)
        ]]

        tree_predictions = np.array([
            tree.predict(features)[0]
            for tree in model.estimators_
        ])

        prediction = float(np.mean(tree_predictions))
        uncertainty = float(np.std(tree_predictions))

        if uncertainty < 0.2:
            confidence = "HIGH"
        elif uncertainty < 0.6:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        results.append({
            "depth": depth,
            "temperature": round(prediction, 3),
            "uncertainty": round(uncertainty, 3),
            "confidence": confidence
        })

    write_result({
        "success": True,
        "results": results
    })

except Exception as error:
    write_result({
        "success": False,
        "error": str(error)
    })
    sys.exit(1)