import sys
import json
import joblib

MODEL_FILE = "ml/models/oceanembed_model.pkl"

try:
    model = joblib.load(MODEL_FILE)

    # Read JSON safely from command line
    raw_input = sys.argv[1]

    print("DEBUG_INPUT:", raw_input, file=sys.stderr)

    input_data = json.loads(raw_input)

    features = [[
        float(input_data["sst"]),
        float(input_data["sss"]),
        float(input_data["ssh"]),
        float(input_data["current_u"]),
        float(input_data["current_v"]),
        float(input_data["wind_u"]),
        float(input_data["wind_v"])
    ]]

    prediction = model.predict(features)[0]

    print(json.dumps({
        "temperature_10m": round(float(prediction), 3)
    }))

except Exception as error:
    print(json.dumps({
        "error": str(error)
    }))
    sys.exit(1)