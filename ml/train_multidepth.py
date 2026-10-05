import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


INPUT_FILE = "data/real/multidepth_features.csv"
MODEL_FILE = "models/oceanembed_multidepth_model.pkl"


print("\n===================================")
print("OCEANEMBED MULTI-DEPTH MODEL")
print("===================================")


# Load dataset
df = pd.read_csv(INPUT_FILE)

print("\nTotal records:", len(df))


# ML input features
features = [
    "sst",
    "sss",
    "ssh",
    "current_u",
    "current_v",
    "wind_u",
    "wind_v",
    "depth"
]

target = "temperature"

X = df[features]
y = df[target]


print("\nFeatures:")
print(features)

print("\nTarget:")
print(target)


# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))


# Create model
print("\nTraining OceanEmbed multi-depth model...")

model = RandomForestRegressor(
    n_estimators=100,
    max_depth=20,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

print("Training completed!")


# Predict
predictions = model.predict(X_test)


# Evaluate
mae = mean_absolute_error(
    y_test,
    predictions
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)


print("\n===================================")
print("OCEANEMBED MODEL RESULTS")
print("===================================")

print(f"\nMAE  : {mae:.3f} °C")
print(f"RMSE : {rmse:.3f} °C")


# Save model
Path("models").mkdir(
    parents=True,
    exist_ok=True
)

joblib.dump(
    model,
    MODEL_FILE
)


print("\nModel saved successfully!")

print("Location:")
print(MODEL_FILE)


print("\n===================================")
print("STEP 21C COMPLETE")
print("===================================")