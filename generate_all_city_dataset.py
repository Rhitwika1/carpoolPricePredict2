import pandas as pd
import random

coords_dict = {
    "Ballygunge":      (22.5226, 88.3715),
    "Dumdum":          (22.6325, 88.4433),
    "Garia":           (22.4495, 88.4113),
    "Howrah":          (22.5892, 88.3104),
    "Salt Lake":       (22.6065, 88.3963),
    "Park Street":     (22.5535, 88.3507),
    "Jadavpur":        (22.4953, 88.3695),
    "Tollygunge":      (22.5019, 88.3420),
    "Behala":          (22.5017, 88.3073),
    "Esplanade":       (22.5637, 88.3508),
    "Shyambazar":      (22.6133, 88.3735),
    "Lake Town":       (22.6067, 88.4043),
    "Kasba":           (22.5204, 88.3882),
    "Barasat":         (22.7206, 88.4807),
    "Baguiati":        (22.6135, 88.4277),
    "Newtown":         (22.5958, 88.4795),
    "Cossipore":       (22.6297, 88.3625),
    "Alipore":         (22.5362, 88.3342),
    "Kankurgachi":     (22.5731, 88.3841),
    "Sodepur":         (22.6996, 88.3734),
    "Baranagar":       (22.6613, 88.3794),
    "Bandel":          (22.9236, 88.3855),
    "Serampore":       (22.7525, 88.3421),
    "Beliaghata":      (22.5631, 88.393)
}
cities = list(coords_dict.keys())

# --- Helper: Haversine distance ---
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

# --- Generate synthetic rides ---
rows = []
fuel_types = ["Diesel", "Petrol", "CNG", "LPG"]
owners = ["Aarav Singh", "Sneha Das", "Priya Sen", "Vikram Sinha", "Neha Patel", "Rohit Menon"]
years = list(range(2012, 2023))
car_names = ["Swift Dzire", "WagonR", "Honda City", "Hyundai i10", "Creta", "XUV500"]
for _ in range(3):  # 3x redundant, more variation, not pure all-to-all
    for pickup in cities:
        for drop in cities:
            if pickup == drop:
                continue
            lat1, lon1 = coords_dict[pickup]
            lat2, lon2 = coords_dict[drop]
            distance = round(haversine(lat1, lon1, lat2, lon2), 2)
            seats = random.choice([4, 5, 6, 7])
            owner = random.choice(owners)
            car_age = 2025 - random.choice(years)
            engine_cc = random.choice([1197, 1248, 1493, 1591, 1798])
            max_power = random.choice([74, 83, 99, 110, 125, 140])
            mileage = random.choice([15, 18, 20, 22])
            fuel_type = random.choice(fuel_types)
            fuel_price = random.choice([95, 98, 99, 108])
            # Add realistic price randomness so model can't overfit!
            price = int(50 + distance * random.uniform(7, 10) + random.randint(-30, 80))
            car_name = random.choice(car_names)
            rows.append({
                "Car_Name": car_name,
                "pickup location": pickup,
                "drop location": drop,
                "travelling distance(km)": distance,
                "fuel type": fuel_type,
                "fuel price": fuel_price,
                "seats": seats,
                "Year of buying": 2025 - car_age,
                "owner": owner,
                "price": price,
                "engine": f"{engine_cc} CC",
                "max_power": f"{max_power} bhp",
                "torque": f"{random.randint(130,250)} Nm",
                "mileage(kmph)": mileage
            })

df = pd.DataFrame(rows)
df.to_csv("car-data-all-locations.csv", index=False)
print(f"✅ New dataset with all locations created: car-data-all-locations.csv ({len(df)} rows)")
