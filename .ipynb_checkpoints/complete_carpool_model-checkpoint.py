import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# SECTION 1: DATA LOADING & PREPROCESSING
# ============================================================================

print("\n" + "="*100)
print("CARPOOL PRICING PREDICTION MODEL - COMPLETE PIPELINE")
print("="*100)

# Load dataset
print("\n[1] Loading dataset...")
car_dataset = pd.read_csv("C:\\CODE\\python projects\\car-price prediction\\csv\\car-data.csv")
print(f"    ✓ Dataset shape: {car_dataset.shape}")
print(f"    ✓ Columns: {len(car_dataset.columns)}")

# Feature Engineering
print("\n[2] Feature Engineering...")
df = car_dataset.copy()
df['car_age'] = 2025 - df['Year of buying']
df['engine_cc'] = pd.to_numeric(
    df['engine'].str.extract(r'(\d+)')[0], 
    errors='coerce'
)
df['power_bhp'] = pd.to_numeric(
    df['max_power'].str.extract(r'(\d+\.?\d*)')[0], 
    errors='coerce'
)
df['price_per_km'] = df['price'] / df['travelling distance(km)']
print("    ✓ Created 4 new features: car_age, engine_cc, power_bhp, price_per_km")

# Drop irrelevant columns
print("\n[3] Dropping Irrelevant Columns...")
columns_to_drop = ['Car_Name', 'Color', 'engine', 'max_power', 'torque', 
                   'mileage(kmph)', 'fuel_unitPrice', 'total_litres']
df_clean = df.drop(columns=columns_to_drop, errors='ignore')
print(f"    ✓ Dropped {len(columns_to_drop)} columns")
print(f"    ✓ Remaining columns: {len(df_clean.columns)}")

# Encode categorical variables
print("\n[4] Encoding Categorical Variables...")
le_fuel = LabelEncoder()
le_owner = LabelEncoder()
le_pickup = LabelEncoder()
le_drop = LabelEncoder()

df_clean['fuel_type_encoded'] = le_fuel.fit_transform(df_clean['fuel type'])
df_clean['owner_encoded'] = le_owner.fit_transform(df_clean['owner'])
df_clean['pickup_encoded'] = le_pickup.fit_transform(df_clean['pickup location'])
df_clean['drop_encoded'] = le_drop.fit_transform(df_clean['drop location'])
print("    ✓ Encoded 4 categorical columns")

# Select features
print("\n[5] Selecting Features for Model...")
feature_columns = [
    'travelling distance(km)',
    'pickup_encoded', 'drop_encoded',
    'fuel_type_encoded', 'fuel price',
    'seats', 'car_age', 'owner_encoded',
    'engine_cc', 'power_bhp'
]
X = df_clean[feature_columns].dropna()
y = df_clean.loc[X.index, 'price']
print(f"    ✓ Selected {len(feature_columns)} features")
print(f"    ✓ Final dataset: {len(X)} samples")

# ============================================================================
# SECTION 2: TRAIN-TEST SPLIT
# ============================================================================

print("\n[6] Splitting Data (80-20 Split)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"    ✓ Training: {len(X_train)} samples")
print(f"    ✓ Testing: {len(X_test)} samples")

# ============================================================================
# SECTION 3: MODEL TRAINING
# ============================================================================

print("\n[7] Training Multiple Models...")

models = {
    'Linear Regression': LinearRegression(),
    'Ridge Regression': Ridge(alpha=1.0),
    'Lasso Regression': Lasso(alpha=0.1),
    'Random Forest': RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1),
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
}

results = []
best_model = None
best_r2 = float('-inf')

for name, model in models.items():
    model.fit(X_train, y_train)

    y_pred_test = model.predict(X_test)
    test_r2 = r2_score(y_test, y_pred_test)
    test_mae = mean_absolute_error(y_test, y_pred_test)

    results.append({'Model': name, 'R²': round(test_r2, 4), 'MAE': round(test_mae, 2)})

    if test_r2 > best_r2:
        best_r2 = test_r2
        best_model = model

    print(f"    ✓ {name:25} | R²: {test_r2:7.4f} | MAE: ₹{test_mae:6.2f}")

# ============================================================================
# SECTION 4: MODEL EVALUATION
# ============================================================================

print("\n[8] Detailed Model Evaluation...")
y_train_pred = best_model.predict(X_train)
y_test_pred = best_model.predict(X_test)

train_r2 = r2_score(y_train, y_train_pred)
test_r2 = r2_score(y_test, y_test_pred)
train_mae = mean_absolute_error(y_train, y_train_pred)
test_mae = mean_absolute_error(y_test, y_test_pred)
test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))

print(f"    Train R² Score: {train_r2:.4f}")
print(f"    Test R² Score: {test_r2:.4f}")
print(f"    Train MAE: ₹{train_mae:.2f}")
print(f"    Test MAE: ₹{test_mae:.2f}")
print(f"    Test RMSE: ₹{test_rmse:.2f}")

# ============================================================================
# SECTION 5: FEATURE IMPORTANCE
# ============================================================================

print("\n[9] Feature Importance Analysis...")
if hasattr(best_model, 'feature_importances_'):
    importances = best_model.feature_importances_
    importance_df = pd.DataFrame({
        'Feature': feature_columns,
        'Importance': importances,
        'Importance_%': (importances * 100).round(2)
    }).sort_values('Importance', ascending=False)

    for idx, row in importance_df.head(5).iterrows():
        print(f"    {row['Feature']:30} | {row['Importance_%']:6.2f}%")

# ============================================================================
# SECTION 6: PRICING PREDICTION FUNCTIONS
# ============================================================================

def predict_carpool_fare(pickup_loc, drop_loc, distance, fuel_type, fuel_price_val,
                        seats_val, car_age_val, owner_type, engine_cc_val=1200, power_bhp_val=75):
    """
    Predict carpool fare using the trained ML model.

    Parameters:
    -----------
    pickup_loc : str - Pickup location name
    drop_loc : str - Drop location name
    distance : float - Travelling distance in kilometers
    fuel_type : str - Fuel type (Diesel/Petrol/CNG/LPG)
    fuel_price_val : int - Current fuel price
    seats_val : int - Number of seats in vehicle
    car_age_val : int - Age of car in years
    owner_type : str - Owner type (First Owner/Second Owner/etc)
    engine_cc_val : float - Engine capacity in CC (default 1200)
    power_bhp_val : float - Power in BHP (default 75)

    Returns:
    --------
    float : Predicted carpool fare in INR
    """
    try:
        pickup_enc = le_pickup.transform([pickup_loc])[0]
        drop_enc = le_drop.transform([drop_loc])[0]
        fuel_enc = le_fuel.transform([fuel_type])[0]
        owner_enc = le_owner.transform([owner_type])[0]
    except:
        return None

    features = np.array([[
        distance, pickup_enc, drop_enc, fuel_enc, fuel_price_val,
        seats_val, car_age_val, owner_enc, engine_cc_val, power_bhp_val
    ]])

    return round(best_model.predict(features)[0], 2)

def calculate_fare_formula(distance, fuel_type='Diesel', passengers=1, peak=False, route='Mixed'):
    """
    Calculate carpool fare using transparent formula.

    Parameters:
    -----------
    distance : float - Distance in km
    fuel_type : str - Diesel/Petrol/CNG/LPG
    passengers : int - Number of passengers sharing
    peak : bool - Peak hour pricing
    route : str - City/Highway/Mixed

    Returns:
    --------
    dict : Detailed fare breakdown
    """
    # Pricing components
    BASE_FARE = 50

    # Distance-based rates
    if distance <= 50: per_km = 3.5
    elif distance <= 150: per_km = 3.0
    elif distance <= 300: per_km = 2.5
    elif distance <= 500: per_km = 2.0
    else: per_km = 1.8

    distance_charge = distance * per_km

    # Multipliers
    fuel_mult = {'Diesel': 1.0, 'Petrol': 0.95, 'CNG': 0.85, 'LPG': 0.90}.get(fuel_type, 1.0)
    share_mult = {1: 1.0, 2: 0.55, 3: 0.40, 4: 0.30}.get(min(passengers, 4), 0.25)
    peak_mult = 1.2 if peak else 1.0
    route_mult = {'Highway': 0.90, 'City': 1.15, 'Mixed': 1.0}.get(route, 1.0)

    # Calculate
    subtotal = BASE_FARE + distance_charge
    total = subtotal * fuel_mult * share_mult * peak_mult * route_mult

    return {
        'base_fare': BASE_FARE,
        'distance_charge': round(distance_charge, 2),
        'subtotal': round(subtotal, 2),
        'fuel_multiplier': fuel_mult,
        'sharing_multiplier': share_mult,
        'peak_multiplier': peak_mult,
        'route_multiplier': route_mult,
        'total_multiplier': round(fuel_mult * share_mult * peak_mult * route_mult, 4),
        'fare_per_person': round(total, 2),
        'total_fare': round(total * passengers, 2)
    }

# ============================================================================
# SECTION 7: EXAMPLE PREDICTIONS
# ============================================================================

print("\n" + "="*100)
print("PREDICTION EXAMPLES")
print("="*100)

print("\n[Example 1] Behala → Park Street (150 km, Diesel, 1 passenger)")
ml_fare = predict_carpool_fare('Behala', 'Park Street', 150, 'Diesel', 550, 5, 3, 'First Owner')
formula_fare = calculate_fare_formula(150, 'Diesel', 1)
print(f"  ML Model Prediction: ₹{ml_fare}")
print(f"  Formula Prediction: ₹{formula_fare['fare_per_person']}")

print("\n[Example 2] Dumdum → Ballygunge (300 km, Petrol, 2 passengers, Peak)")
formula_fare2 = calculate_fare_formula(300, 'Petrol', 2, peak=True)
print(f"  Per Person: ₹{formula_fare2['fare_per_person']}")
print(f"  Total (both): ₹{formula_fare2['total_fare']}")

print("\n[Example 3] Salt Lake → Rajarhat (500 km, CNG, 3 passengers, Highway)")
formula_fare3 = calculate_fare_formula(500, 'CNG', 3, route='Highway')
print(f"  Per Person: ₹{formula_fare3['fare_per_person']}")
print(f"  Total (3 people): ₹{formula_fare3['total_fare']}")

print("\n" + "="*100)
print("✓ MODEL PIPELINE COMPLETE!")
print("="*100)
print("\nModel ready for deployment. Use predict_carpool_fare() for predictions.")
