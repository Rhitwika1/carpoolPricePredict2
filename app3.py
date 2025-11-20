import streamlit as st
import pandas as pd
import pickle
import openrouteservice
from openrouteservice import convert
import folium
from streamlit_folium import st_folium

# ---- API Key for OpenRouteService -----
ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImJkZDEyN2FlMGNmMzQ5MWFiZDRiYzczYTA2Y2E2OWRlIiwiaCI6Im11cm11cjY0In0="

# ---- Styles ----
st.set_page_config(page_title="RideShare", page_icon="🚗", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
        body { background-color: #f5f7fa; }
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

# ---- Data Load ----
@st.cache_resource
def load_data():
    df = pd.read_csv("car-data.csv")
    # Add random owners, times, ratings for 8000+ rows if needed
    return df

df = load_data()

# ---- Get coordinates ----
coords_dict = {
    'Ballygunge': (22.5226, 88.3715),
    'Dumdum': (22.6325, 88.4433),
    'Garia': (22.4495, 88.4113),
    'Howrah': (22.5892, 88.3104),
    'Salt Lake':  (22.6065, 88.3963),
    "Park Street":(22.5535, 88.3507),
    "Jadavpur":   (22.4953, 88.3695),
    "Tollygunge": (22.5019, 88.3420),
    "Behala":     (22.5017, 88.3073),
    "Esplanade":  (22.5637, 88.3508),
    "Shyambazar": (22.6133, 88.3735),
    "Lake Town":  (22.6067, 88.4043),
    "Kasba":      (22.5204, 88.3882),
    "Barasat":    (22.7206, 88.4807),
    "Baguiati":   (22.6135, 88.4277),
    "Newtown":    (22.5958, 88.4795),
    "Cossipore":  (22.6297, 88.3625),
    "Alipore":    (22.5362, 88.3342),
    "Kankurgachi":(22.5731, 88.3841),
    "Sodepur":    (22.6996, 88.3734),
    "Baranagar":  (22.6613, 88.3794),
    "Bandel":     (22.9236, 88.3855),
    "Serampore":  (22.7525, 88.3421),
    "Beliaghata": (22.5631, 88.393)
    
}

# ---- Fare calculation model (as per your formula) ----
def calc_fare(distance_km):
    base = 50
    if distance_km <= 50:
        per_km = 8.5
    elif distance_km <= 100:
        per_km = 7.5
    elif distance_km <= 150:
        per_km = 6.5
    elif distance_km <= 200:
        per_km = 5.5
    else:
        per_km = 4.5
    return int(base + distance_km * per_km)

# ---- App Layout ----
st.markdown("<div class='big-title'>👋 Welcome back, User!</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Share rides, save money, and reduce your carbon footprint. Find real carpools on realistic routes!</div>", unsafe_allow_html=True)

st.markdown("""
    <div class='highlight-card'>
        <span>👥 <b>10,000+ Users</b></span> &nbsp;
        <span>💸 <b>Save up to 70%</b></span> &nbsp;
        <span>🌍 <b>Eco-Friendly</b></span>
    </div>
""", unsafe_allow_html=True)

st.write("")

col1, col2, col3, col4 = st.columns([2,2,2,1])
with col1: pickup = st.selectbox("From (City)", list(coords_dict.keys()))
with col2: drop = st.selectbox("To (City)", list(coords_dict.keys()))
with col3: date = st.date_input("Date")
with col4: 
    if st.button("Search Rides", use_container_width=True): 
        st.session_state['show_results'] = True

if st.session_state.get('show_results', False):

    # ---- Actual Route ----
    if pickup == drop:
        st.error("Pickup and Drop location cannot be the same.")
    elif pickup not in coords_dict or drop not in coords_dict:
        st.warning("Coordinates not available for route.")
    else:
        org_coords = (coords_dict[pickup][1], coords_dict[pickup][0])  
        dest_coords = (coords_dict[drop][1], coords_dict[drop][0])

        client = openrouteservice.Client(key=ORS_API_KEY)
        try:
            # (lng, lat) order!
            coords = [org_coords, dest_coords] 
            routes = client.directions(coords, profile='driving-car', format='geojson')
            geom = routes['features'][0]['geometry']
            distance_km = routes['features'][0]['properties']['segments'][0]['distance'] / 1000
            duration_min = routes['features'][0]['properties']['segments'][0]['duration'] / 60
            # -- Map
            line = folium.GeoJson(geom, style_function=lambda x: {'color': '#0066ff', 'weight': 5}).get_bounds()
            map_center = [(coords_dict[pickup][0] + coords_dict[drop][0])/2, (coords_dict[pickup][1] + coords_dict[drop][1])/2]
            m = folium.Map(location=map_center, zoom_start=12, tiles="CartoDB Positron")
            folium.Marker(coords_dict[pickup], popup="Start", icon=folium.Icon(color="green")).add_to(m)
            folium.Marker(coords_dict[drop], popup="End", icon=folium.Icon(color="red")).add_to(m)
            folium.GeoJson(geom, name="route", style_function=lambda x: {'color':'#0066ff', 'weight': 5, 'dashArray': '9'}).add_to(m)
            st_folium(m, height=480, use_container_width=True)
            # Big Route details
            st.markdown(f"""<div style="font-size:22px;font-weight:700;margin-top:10px;color:#764ba2;">
            📍 Route Details:<br>
            <span style="color:#29be5a;font-size:19px;">🟢 {pickup}</span> <span style="font-size:15px; color:#999;">({coords_dict[pickup][0]}, {coords_dict[pickup][1]})</span><br>
            <span style="color:#f54b4b;font-size:19px;">🔴 {drop}</span> <span style="font-size:15px; color:#999;">({coords_dict[drop][0]}, {coords_dict[drop][1]})</span><br>
            <span style="color:#0066ff;font-size:18px;">🔵 Blue route line shows the path</span>
            </div>""", unsafe_allow_html=True)

            # Distance and time
            st.markdown(f"**Distance:** `{distance_km:.2f} km`   |   **Estimated Time:** `{duration_min:.0f} min`   |   **Date:** `{date.strftime('%b %d, %Y')}`")

            # New price
            fair_price = calc_fare(distance_km)
            st.markdown(f"<div class='price-main'>₹{fair_price} <span style='font-size:22px;color:#666;font-weight:400;'>per seat</span></div>", unsafe_allow_html=True)

        except Exception as e:
            st.error("Failed to get realistic route. (API key correct? Cities valid?)")

    # Cards for available rides (demo, can be enhanced)
    st.markdown(f"### Available Rides")
    sample_names = [("Aarav Singh", 4.7), ("Krishna Verma", 4.5), ("Sneha Das", 4.2), ("Priya Sen", 4.8)]
    for name, rating in sample_names:
        with st.container():
            st.markdown(
    f"<div class='card'><b>{name}</b> &nbsp; ⭐ <b>{rating}</b><br>"
    f"🟢 <b>From:</b> {pickup} &nbsp; 🔴 <b>To:</b> {drop}<br>"
    f"🗓️ <b>Date:</b> {date.strftime('%b %d, %Y')}<br>"
    f"<span style='font-size:1.2rem; color:#02ac5a;font-weight:700;'>₹{fair_price} per seat</span></div>",
    unsafe_allow_html=True
)


    st.session_state['show_results'] = True  # So user must click search again for new results

else:
    st.info("Select pickup, drop, and date, then click Search Rides.")

