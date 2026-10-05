import sys
import json
import joblib

MODEL_FILE = "ml/models/oceanembed_model.pkl"

DEPTHS = [
    0, 5, 10, 20, 30, 50, 75,
    100, 125, 150, 200, 300,
    500, 700, 1000
]

try:
    # Read JSON from stdin
    raw_input = sys.stdin.read()

    if not raw_input.strip():
        raise ValueError("No input data received from Next.js.")

    input_data = json.loads(raw_input)

    model = joblib.load(MODEL_FILE)

    features = [[
        float(input_data["sst"]),
        float(input_data["sss"]),
        float(input_data["ssh"]),
        float(input_data["current_u"]),
        float(input_data["current_v"]),
        float(input_data["wind_u"]),
        float(input_data["wind_v"])
    ]]

    base_temperature = float(
        model.predict(features)[0]
    )

    profile = []

    for depth in DEPTHS:

        if depth == 0:
            temperature = base_temperature + 1.5
        elif depth <= 10:
            temperature = base_temperature
        elif depth <= 30:
            temperature = base_temperature - 0.5
        elif depth <= 50:
            temperature = base_temperature - 1.2
        elif depth <= 75:
            temperature = base_temperature - 2.0
        elif depth <= 100:
            temperature = base_temperature - 2.8
        elif depth <= 150:
            temperature = base_temperature - 4.0
        elif depth <= 200:
            temperature = base_temperature - 5.0
        elif depth <= 300:
            temperature = base_temperature - 6.5
        elif depth <= 500:
            temperature = base_temperature - 8.0
        elif depth <= 700:
            temperature = base_temperature - 9.0
        else:
            temperature = base_temperature - 10.0

        profile.append({
            "depth": depth,
            "temperature": round(
                temperature,
                3
            )
        })

    print(json.dumps({
        "success": True,
        "profile": profile
    }))

except Exception as error:

    print(json.dumps({
        "success": False,
        "error": str(error)
    }))

    sys.exit(1)