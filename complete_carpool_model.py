import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import pickle

# ----- DATA LOADING -----
df = pd.read_csv("car-data-all-locations.csv")  # <-- Use your all-locations CSV

# ----- FEATURE ENGINEERING -----
df['engine_cc'] = df['engine'].str.extract(r'(\d+)').astype(float)
df['max_power_bhp'] = df['max_power'].str.extract(r'(\d+\.?\d*)').astype(float)
df['mileage'] = pd.to_numeric(df['mileage(kmph)'], errors='coerce')
df['car_age'] = 2025 - df['Year of buying']

# Drop irrelevant/redundant columns with safety check
to_drop = [
    'Car_Name', 'engine', 'max_power', 'torque', 'fuel_unitPrice',
    'mileage(kmph)', 'total_litres', 'car_number', 'owner_name'
]
df = df.drop([col for col in to_drop if col in df.columns], axis=1)

# Fill missing categorical values
for col in ['fuel type', 'pickup location', 'drop location', 'owner']:
    if col in df.columns:
        df[col] = df[col].fillna("Unknown")

# Fill missing numeric values with median
num_cols = [
    'engine_cc', 'max_power_bhp', 'mileage', 'car_age',
    'seats', 'fuel price', 'travelling distance(km)'
]
for col in num_cols:
    if col in df.columns:
        df[col] = df[col].fillna(df[col].median())

# ----- CATEGORICAL ENCODING -----
encoders = {}
cat_cols = ['fuel type', 'pickup location', 'drop location', 'owner']
for col in cat_cols:
    if col in df.columns:
        enc = LabelEncoder()
        df[col] = enc.fit_transform(df[col])
        encoders[col] = enc

# ----- SELECT FEATURES & TARGET -----
assert 'price' in df.columns, "Error: 'price' column is missing in data!"
X = df.drop('price', axis=1)
y = df['price']

# ----- TRAIN/TEST SPLIT -----
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)

# ----- MODEL TRAINING -----
model = RandomForestRegressor(n_estimators=200, max_depth=14, random_state=42)
model.fit(X_train, y_train)

# ----- MODEL EVALUATION -----
def reg_results(y_true, y_pred, split="Train"):
    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    print(f"[{split}]    R2: {r2:.3f}   MAE: {mae:.2f}   RMSE: {rmse:.2f}")
    return r2, mae, rmse

print("\nResults:")
reg_results(y_train, model.predict(X_train), split="Train")
reg_results(y_test, model.predict(X_test), split="Test")

# ----- FEATURE IMPORTANCE PLOT -----
plt.figure(figsize=(10, 5))
fi = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
fi.plot(kind='bar')
plt.title("Feature Importance")
plt.tight_layout()
plt.show()

# ----- SAVE MODEL & ENCODERS -----
with open("carpool_model.pkl", "wb") as f_model:
    pickle.dump(model, f_model)
with open("encoders.pkl", "wb") as f_enc:
    pickle.dump(encoders, f_enc)
print("✅ Model and encoders saved to carpool_model.pkl and encoders.pkl.")

# Save column order to ensure app prediction input consistency
with open("model_columns.pkl", "wb") as f_cols:
    pickle.dump(list(X.columns), f_cols)
print("✅ Model columns saved for prediction input consistency.")


'''
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import pickle
import re

# ----- DATA LOADING -----
df = pd.read_csv("car-data.csv")

# ----- FEATURE ENGINEERING -----
df['engine_cc'] = df['engine'].str.extract(r'(\d+)').astype(float)
df['max_power_bhp'] = df['max_power'].str.extract(r'(\d+\.?\d*)').astype(float)
df['mileage'] = pd.to_numeric(df['mileage(kmph)'], errors='coerce')
df['car_age'] = 2025 - df['Year of buying']

# Drop irrelevant/redundant columns with safety check
to_drop = [
    'Car_Name', 'engine', 'max_power', 'torque', 'fuel_unitPrice',
    'mileage(kmph)', 'total_litres', 'car_number', 'owner_name'
]
df = df.drop([col for col in to_drop if col in df.columns], axis=1)

# Fill missing categorical values
for col in ['fuel type', 'pickup location', 'drop location', 'owner']:
    # Ensure the column exists before filling
    if col in df.columns:
        df[col] = df[col].fillna("Unknown")

# Fill missing numeric values with median
num_cols = [
    'engine_cc', 'max_power_bhp', 'mileage', 'car_age',
    'seats', 'fuel price', 'travelling distance(km)'
]
for col in num_cols:
    if col in df.columns:
        df[col] = df[col].fillna(df[col].median())

# ----- CATEGORICAL ENCODING -----
encoders = {}
cat_cols = ['fuel type', 'pickup location', 'drop location', 'owner']
for col in cat_cols:
    if col in df.columns:
        enc = LabelEncoder()
        df[col] = enc.fit_transform(df[col])
        encoders[col] = enc

# ----- SELECT FEATURES & TARGET -----
assert 'price' in df.columns, "Error: 'price' column is missing in data!"
X = df.drop('price', axis=1)
y = df['price']

# ----- TRAIN/TEST SPLIT -----
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)

# ----- MODEL TRAINING -----
model = RandomForestRegressor(n_estimators=200, max_depth=14, random_state=42)
model.fit(X_train, y_train)

# ----- MODEL EVALUATION -----
def reg_results(y_true, y_pred, split="Train"):
    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    print(f"[{split}]    R2: {r2:.3f}   MAE: {mae:.2f}   RMSE: {rmse:.2f}")
    return r2, mae, rmse

print("\nResults:")
reg_results(y_train, model.predict(X_train), split="Train")
reg_results(y_test, model.predict(X_test), split="Test")

# ----- FEATURE IMPORTANCE PLOT -----
try:
    fi = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
    plt.figure(figsize=(10, 5))
    fi.plot(kind='bar')
    plt.title("Feature Importance")
    plt.tight_layout()
    plt.show()
except Exception as e:
    print(f"Feature importance plot error: {e}")

# ----- SAVE MODEL & ENCODERS -----
with open("carpool_model.pkl", "wb") as f_model:
    pickle.dump(model, f_model)
with open("encoders.pkl", "wb") as f_enc:
    pickle.dump(encoders, f_enc)
print("✅ Model and encoders saved to carpool_model.pkl and encoders.pkl.")

# ----- OPTIONAL: Save columns order as meta (for inference in streamlit/app) -----
with open("model_columns.pkl", "wb") as f_cols:
    pickle.dump(list(X.columns), f_cols)
print("✅ Model columns saved for prediction input consistency.")
'''


'''
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import pickle
import re

# ----- DATA LOADING -----
df = pd.read_csv("car-data.csv")

# ----- FEATURE ENGINEERING -----
df['engine_cc'] = df['engine'].str.extract(r'(\d+)').astype(float)
df['max_power_bhp'] = df['max_power'].str.extract(r'(\d+\.?\d*)').astype(float)
df['mileage'] = pd.to_numeric(df['mileage(kmph)'], errors='coerce')
df['car_age'] = 2025 - df['Year of buying']

# Drop irrelevant or redundant columns
to_drop = [
    'Car_Name', 'engine', 'max_power', 'torque', 'fuel_unitPrice',
    'mileage(kmph)', 'total_litres', 'car_number', 'owner_name'
]
df = df.drop([col for col in to_drop if col in df.columns], axis=1)

# Fill missing values
for col in ['fuel type', 'pickup location', 'drop location', 'owner']:
    df[col] = df[col].fillna("Unknown")

num_cols = [
    'engine_cc', 'max_power_bhp', 'mileage', 'car_age',
    'seats', 'fuel price', 'travelling distance(km)'
]
for col in num_cols:
    df[col] = df[col].fillna(df[col].median())

# ----- CATEGORICAL ENCODING -----
encoders = {}
cat_cols = ['fuel type', 'pickup location', 'drop location', 'owner']
for col in cat_cols:
    enc = LabelEncoder()
    df[col] = enc.fit_transform(df[col])
    encoders[col] = enc

# ----- SELECT FEATURES & TARGET -----
X = df.drop('price', axis=1)
y = df['price']

# ----- TRAIN/TEST SPLIT -----
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)

# ----- MODEL TRAINING -----
model = RandomForestRegressor(n_estimators=200, max_depth=14, random_state=42)
model.fit(X_train, y_train)

# ----- MODEL EVALUATION -----
def reg_results(y_true, y_pred, split="Train"):
    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    print(f"[{split}]    R2: {r2:.3f}   MAE: {mae:.2f}   RMSE: {rmse:.2f}")
    return r2, mae, rmse

print("\nResults:")
reg_results(y_train, model.predict(X_train), split="Train")
reg_results(y_test, model.predict(X_test), split="Test")

# ----- FEATURE IMPORTANCE -----
fi = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
plt.figure(figsize=(10,5))
fi.plot(kind='bar')
plt.title("Feature Importance")
plt.show()

# ----- SAVE MODEL & ENCODERS -----
with open("carpool_model.pkl", "wb") as f_model:
    pickle.dump(model, f_model)

with open("encoders.pkl", "wb") as f_enc:
    pickle.dump(encoders, f_enc)

print("Model and encoders saved to carpool_model.pkl and encoders.pkl.")
'''