import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split


# ==========================================
# 1. LOAD DATA
# ==========================================

data_file = "ml/data/real/oceanembed_training_demo.csv"

print("\nLoading OceanEmbed training data...")

data = pd.read_csv(data_file)

print(f"Total records: {len(data)}")


# ==========================================
# 2. SELECT INPUT FEATURES
# ==========================================

features = [
    "sst",
    "sss",
    "ssh",
    "current_u",
    "current_v",
    "wind_u",
    "wind_v"
]

target = "temperature_10m"

X = data[features]
y = data[target]


# ==========================================
# 3. SPLIT DATA
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))


# ==========================================
# 4. CREATE MODEL
# ==========================================

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)


# ==========================================
# 5. TRAIN MODEL
# ==========================================

print("\nTraining OceanEmbed model...")

model.fit(X_train, y_train)

print("Training completed!")


# ==========================================
# 6. MAKE PREDICTIONS
# ==========================================

predictions = model.predict(X_test)


# ==========================================
# 7. EVALUATE MODEL
# ==========================================

mae = mean_absolute_error(
    y_test,
    predictions
)

mse = mean_squared_error(
    y_test,
    predictions
)

rmse = mse ** 0.5


print("\n===================================")
print("OCEANEMBED MODEL RESULTS")
print("===================================")

print(f"MAE  : {mae:.3f} °C")
print(f"RMSE : {rmse:.3f} °C")


# ==========================================
# 8. SAVE MODEL
# ==========================================

model_file = "ml/models/oceanembed_model.pkl"

joblib.dump(
    model,
    model_file
)

print("\nModel saved successfully!")
print(f"Location: {model_file}")