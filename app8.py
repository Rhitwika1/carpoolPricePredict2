import streamlit as st
import pandas as pd
import pickle
import openrouteservice
from openrouteservice import convert
import folium
from streamlit_folium import st_folium
import random
from datetime import time, datetime, date as date_module, timedelta
import numpy as np

# ---- API Key for OpenRouteService -----
ORS_API_KEY = st.secrets["ORS_API_KEY"]


# ---- Load model/encoders/data ----
with open("carpool_model.pkl", "rb") as f_model:
    model = pickle.load(f_model)
with open("encoders.pkl", "rb") as f_enc:
    encoders = pickle.load(f_enc)
df = pd.read_csv("car-data.csv")

# ---- Coordinates ----
coords_dict = { "Ballygunge":      (22.5226, 88.3715),
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

 }  # Use your full coords from app7.py

# ---- Only allow cities known to encoder ----
allowed_pickups = sorted(list(encoders['pickup location'].classes_))
allowed_drops = sorted(list(encoders['drop location'].classes_))

# ---- Styles/Title ----
st.set_page_config(page_title="RideShare", page_icon="🚗", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
        .big-title { font-size: 2.2rem; font-weight: 700; color: #667eea; margin-bottom: 0.5rem; }
        .subtitle { font-size: 16px; color: #555; margin-bottom: 1.2rem; font-weight: 500;}
        .highlight-card { border: 2px solid #667eea; border-radius: 12px; padding: 1.5em; background-color: #e3eaff;}
        .route-details { font-size: 20px !important; font-weight: 600;}
        .route-coords { font-size: 17px !important; color: #222; }
        .section-title { font-size: 17px; margin-bottom: 13px; font-weight:700; color:#764ba2;}
        .price-main { font-size: 2.5rem; font-weight: bold; color: #02ac5a;}
        .card { border-radius: 15px; background: #fff; box-shadow: 0 2px 10px rgba(0,0,0,0.06); padding: 1.2em; margin-bottom: 18px;}
    </style>
""", unsafe_allow_html=True)
st.markdown("<div class='big-title'>👋 Welcome back, User!</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Share rides, save money... realistic carpools on real routes!</div>", unsafe_allow_html=True)

st.markdown("""
    <div class='highlight-card'>
        <span>👥 <b>10,000+ Users</b></span> &nbsp;
        <span>💸 <b>Save up to 70%</b></span> &nbsp;
        <span>🌍 <b>Eco-Friendly</b></span>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
with col1:
    pickup = st.selectbox("From (City)", allowed_pickups)
with col2:
    drop = st.selectbox("To (City)", allowed_drops)
with col3:
    selected_date = st.date_input("Date", min_value=date_module.today())
with col4:
    ride_time = st.time_input("Time", value=time(9, 0))
with col5:
    if st.button("Search Rides", use_container_width=True):
        now = datetime.now()
        selected_datetime = datetime.combine(selected_date, ride_time)
        if selected_datetime < now:
            st.error(f"Cannot book rides in the past!")
        elif pickup == drop:
            st.error("Pickup and Drop location cannot be the same.")
        else:
            st.session_state['show_results'] = True
            st.session_state['pickup'] = pickup
            st.session_state['drop'] = drop
            st.session_state['date'] = selected_date
            st.session_state['time'] = ride_time

if st.session_state.get('show_results', False):
    pickup = st.session_state['pickup']
    drop = st.session_state['drop']
    date = st.session_state['date']
    ride_time = st.session_state['time']
    if pickup not in coords_dict or drop not in coords_dict:
        st.warning("Coordinates not available for route.")
    else:
        org_coords = (coords_dict[pickup][1], coords_dict[pickup][0])
        dest_coords = (coords_dict[drop][1], coords_dict[drop][0])
        client = openrouteservice.Client(key=ORS_API_KEY)
        try:
            coords = [org_coords, dest_coords]
            routes = client.directions(coords, profile='driving-car', format='geojson')
            geom = routes['features'][0]['geometry']
            distance_km = routes['features'][0]['properties']['segments'][0]['distance'] / 1000
            duration_min = routes['features'][0]['properties']['segments'][0]['duration'] / 60

            map_center = [(coords_dict[pickup][0] + coords_dict[drop][0])/2, (coords_dict[pickup][1] + coords_dict[drop][1])/2]
            m = folium.Map(location=map_center, zoom_start=12, tiles="CartoDB Positron")
            folium.Marker(coords_dict[pickup], popup="Start", icon=folium.Icon(color="green")).add_to(m)
            folium.Marker(coords_dict[drop], popup="End", icon=folium.Icon(color="red")).add_to(m)
            folium.GeoJson(geom, name="route", style_function=lambda x: {'color':'#0066ff', 'weight': 5, 'dashArray': '9'}).add_to(m)
            st_folium(m, height=480, use_container_width=True)

            st.markdown(f"""<div style="font-size:22px;font-weight:700;margin-top:10px;color:#764ba2;">
            📍 Route Details:<br>
            <span style="color:#29be5a;font-size:19px;">🟢 {pickup}</span> <span style="font-size:15px; color:#999;">({coords_dict[pickup][0]}, {coords_dict[pickup][1]})</span><br>
            <span style="color:#f54b4b;font-size:19px;">🔴 {drop}</span> <span style="font-size:15px; color:#999;">({coords_dict[drop][0]}, {coords_dict[drop][1]})</span><br>
            <span style="color:#0066ff;font-size:18px;">🔵 Blue route line shows the path</span></div>""", unsafe_allow_html=True)

            st.markdown(f"**Distance:** `{distance_km:.2f} km`   |   **Estimated Time:** `{duration_min:.0f} min`   |   **Date:** `{date.strftime('%b %d, %Y')}`   |   **Time:** `{ride_time.strftime('%I:%M %p')}`")

            # --------- ML Model-based fare prediction ---------
            # Use median for other features, encode pickup/drop
            median_vals = df.median(numeric_only=True)
            input_dict = {
                "pickup location": encoders['pickup location'].transform([pickup])[0],
                "drop location": encoders['drop location'].transform([drop])[0],
                "travelling distance(km)": distance_km,
                "fuel type": median_vals['fuel type'],
                "fuel price": median_vals['fuel price'],
                "seats": median_vals['seats'],
                "car_age": median_vals['car_age'],
                "owner": median_vals['owner'],
                "engine_cc": median_vals['engine_cc'],
                "max_power_bhp": median_vals['max_power_bhp'],
                "mileage": median_vals['mileage'],
            }
            input_order = [col for col in df.drop('price', axis=1).columns]
            input_values = np.array([input_dict[col] for col in input_order]).reshape(1, -1)
            fair_price = int(model.predict(input_values)[0])

        except Exception as e:
            #st.error("Failed to get realistic route. (API key correct? Cities valid?)")
            distance_km = 12
            duration_min = 30
            fair_price = 300

        # ---- Time slots ----
        available_time_slots = [
            f"{(datetime.combine(datetime.today(), ride_time) + timedelta(minutes=offset)).strftime('%I:%M %p')}"
            for offset in [-60, -30, 0, 30]
        ]

        # ---- Sample drivers and rides ----
        st.markdown(f"### Available Rides")
        sample_names = [("Aarav Singh", 4.7), ("Krishna Verma", 4.5), ("Sneha Das", 4.2), ("Priya Sen", 4.8)]
        price_modifiers = [0.85, 0.95, 1.0, 1.1, 1.15, 1.25, 1.3]
        used_mods = set()
        for idx, (name, rating) in enumerate(sample_names):
            while True:
                mod = random.choice(price_modifiers)
                if mod not in used_mods or len(used_mods) == len(price_modifiers):
                    used_mods.add(mod)
                    break
            slot = available_time_slots[idx % len(available_time_slots)]
            driver_price = int(fair_price * mod)
            st.markdown(
                f"""<div class='card'>
                <b>{name}</b> &nbsp; ⭐ <b>{rating}</b><br>
                🟢 <b>From:</b> {pickup} &nbsp; 🔴 <b>To:</b> {drop}<br>
                🗓️ <b>Date:</b> {date.strftime('%b %d, %Y')} &nbsp; 🕐 <b>Time:</b> {slot}<br>
                <span style='font-size:1.2rem; color:#02ac5a;font-weight:700;'>₹{driver_price} per seat</span>
                </div>""",
                unsafe_allow_html=True
            )
else:
    st.info("Select pickup, drop, date, and time, then click Search Rides.")
