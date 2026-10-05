import sys
import json
import warnings
from pathlib import Path
import joblib

warnings.filterwarnings(
    "ignore",
    message="X does not have valid feature names.*",
    category=UserWarning,
)

MODEL_FILE = "ml/models/oceanembed_multidepth_model.pkl"
OUTPUT_PATH = sys.argv[2] if len(sys.argv) > 2 else None

DEPTHS = [
    0, 5, 10, 20, 30,
    50, 75, 100, 125,
    150, 200, 300, 500,
    700, 1000
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

    profile = []

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

        prediction = model.predict(features)[0]

        profile.append({
            "depth": depth,
            "temperature": round(float(prediction), 3)
        })

    write_result({
        "success": True,
        "profile": profile
    })

except Exception as error:
    write_result({
        "success": False,
        "error": str(error)
    })
    sys.exit(1)