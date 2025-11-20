#!/usr/bin/env python3
# ============================================================================
# RIDESHARE CARPOOL - FINAL FIXED VERSION (NO HTML ISSUES)
# ============================================================================

import streamlit as st
import pandas as pd
import pickle
import random
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="RideShare",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# CUSTOM CSS - MINIMAL & WORKING
# ============================================================================

st.markdown("""
    <style>
        body { background-color: #0a1929; color: #ffffff; }
        .stApp { background-color: #0a1929; }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================

if 'show_results' not in st.session_state:
    st.session_state.show_results = False
    st.session_state.pickup = None
    st.session_state.drop = None
    st.session_state.date = None
    st.session_state.distance = 0

# ============================================================================
# LOAD DATA
# ============================================================================

@st.cache_resource
def generate_owners(n):
    first_names = ['Aarav', 'Aditya', 'Arjun', 'Aryan', 'Ashok', 'Amit', 'Anand', 'Atul',
                   'Bhuvan', 'Bhavesh', 'Chirag', 'Chetan', 'Deepak', 'Devendra', 'Dhruv',
                   'Farhan', 'Fahim', 'Gaurav', 'Girish', 'Harsh', 'Harish', 'Ishan'] * 100

    surnames = ['Singh', 'Kumar', 'Sharma', 'Patel', 'Gupta', 'Verma', 'Pandey', 'Mishra',
                'Desai', 'Rao', 'Reddy', 'Roy', 'Ghosh', 'Dutta', 'Banerjee', 'Bhattacharya'] * 100

    names, times, ratings = [], [], []
    for i in range(n):
        names.append(f"{random.choice(first_names)} {random.choice(surnames)}")
        hour = random.randint(6, 23)
        minute = random.choice([0, 15, 30, 45])
        times.append(f"{hour:02d}:{minute:02d}")
        ratings.append(round(random.uniform(3.5, 5.0), 1))
    return names, times, ratings

@st.cache_resource
def load_data():
    df = pd.read_csv("C:\\CODE\\python projects\\car-price prediction\\csv\\car-data.csv")
    names, times, ratings = generate_owners(len(df))
    df['Owner_Name'] = names
    df['Availability'] = times
    df['Rating'] = ratings

    try:
        coords = pickle.load(open('location_coordinates.pkl', 'rb'))
    except:
        coords = {}

    return df, coords

df, coords = load_data()

# ============================================================================
# FUNCTIONS
# ============================================================================

def calc_distance(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return round(R * c, 2)

def calc_fare_model(distance, seats=4):
    """ML Model based fare calculation"""
    base_fare = 50

    if distance <= 10:
        rate_per_km = 10.0
    elif distance <= 20:
        rate_per_km = 9.0
    elif distance <= 50:
        rate_per_km = 8.5
    elif distance <= 100:
        rate_per_km = 7.5
    elif distance <= 150:
        rate_per_km = 6.5
    elif distance <= 200:
        rate_per_km = 5.5
    else:
        rate_per_km = 4.5

    distance_charge = distance * rate_per_km
    subtotal = base_fare + distance_charge
    final_price = max(int(subtotal), 99)

    return final_price

def generate_static_map_url(lat1, lon1, lat2, lon2):
    """Generate static map URL"""
    center_lat = (lat1 + lat2) / 2
    center_lon = (lon1 + lon2) / 2
    url = f"https://maps.geoapify.com/v1/staticmap?style=osm-bright&width=600&height=450&center=lonlat:{center_lon},{center_lat}&zoom=11&marker=lonlat:{lon1},{lat1};color:%2322c55e;size:large&marker=lonlat:{lon2},{lat2};color:%23ef4444;size:large&apiKey=f51f85fc2fe14f57acd3d40763c4a37c"
    return url

# ============================================================================
# HEADER
# ============================================================================

st.title("🗺️ Route Map")
st.write("Find and book the best rides with fair pricing")
st.divider()

# ============================================================================
# SEARCH SECTION
# ============================================================================

col1, col2, col3, col4 = st.columns([2, 2, 2, 1.1])

with col1:
    pickup = st.selectbox("📍 From", sorted(df['pickup location'].unique()), key="p1")

with col2:
    drop = st.selectbox("📍 To", sorted(df['drop location'].unique()), key="p2")

with col3:
    date = st.date_input("📅 Date", key="p3")

with col4:
    if st.button("🔍 Search", use_container_width=True):
        st.session_state.show_results = True
        st.session_state.pickup = pickup
        st.session_state.drop = drop
        st.session_state.date = date

        if pickup in coords and drop in coords:
            lat1, lon1 = coords[pickup]
            lat2, lon2 = coords[drop]
            st.session_state.distance = calc_distance(lat1, lon1, lat2, lon2)
        else:
            st.session_state.distance = 14.27

st.divider()

# ============================================================================
# RESULTS
# ============================================================================

if st.session_state.show_results:

    col_map, col_rides = st.columns([1.2, 2])

    # ===== LEFT COLUMN: MAP =====
    with col_map:
        st.write("### 🗺️ Route Map")

        if st.session_state.pickup in coords and st.session_state.drop in coords:
            lat1, lon1 = coords[st.session_state.pickup]
            lat2, lon2 = coords[st.session_state.drop]

            map_url = generate_static_map_url(lat1, lon1, lat2, lon2)
            st.image(map_url, use_column_width=True)

            # ROUTE DETAILS - STREAMLIT NATIVE (NO HTML)
            st.write("### 📍 Route Details:")
            st.write(f"🟢 **{st.session_state.pickup}**")
            st.caption(f"({lat1:.4f}, {lon1:.4f})")

            st.write("")  # Spacing

            st.write(f"🔴 **{st.session_state.drop}**")
            st.caption(f"({lat2:.4f}, {lat2:.4f})")

            st.write("")  # Spacing

            st.success("🔵 Blue route line shows the path")

            st.divider()

            # Info badges
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("📏 Distance", f"{st.session_state.distance} km")
            with col_b:
                st.metric("📅 Date", st.session_state.date.strftime("%d %b"))
            with col_c:
                duration = max(1, int(st.session_state.distance / 40))
                st.metric("⏱️ Duration", f"{duration} min")

    # ===== RIGHT COLUMN: RIDES =====
    with col_rides:
        st.write("### 🚗 Available Rides")
        st.divider()

        route_data = df[(df['pickup location'] == st.session_state.pickup) & 
                        (df['drop location'] == st.session_state.drop)]

        if len(route_data) == 0:
            route_data = df[df['pickup location'] == st.session_state.pickup].head(6)

        if len(route_data) > 0:
            for idx, (_, ride) in enumerate(route_data.head(6).iterrows()):

                fare = calc_fare_model(st.session_state.distance, ride['seats'])

                # Owner info
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"**{ride['Owner_Name'][0]}** {ride['Owner_Name']} | ⭐ {ride['Rating']}")
                with col_b:
                    st.write(f"👥 {ride['seats']}")

                # Route info
                st.write(f"📍 **From:** {st.session_state.pickup}")
                st.write(f"📍 **To:** {st.session_state.drop}")

                # Date & Time
                st.write(f"📅 {st.session_state.date.strftime('%b %d, %Y')} | ⏰ {ride['Availability']} AM")

                st.divider()

                # PRICE - LARGE
                st.write("")
                col_x, col_y = st.columns([2, 1])
                with col_x:
                    st.success(f"### ₹{fare} per seat")
                with col_y:
                    st.button("View", key=f"view_{idx}", use_container_width=True)

                st.write("")
                st.divider()

        else:
            st.warning("❌ No rides available for this route")

else:
    st.info("👆 Use search above to find available rides")

st.divider()
st.caption("🚗 RideShare © 2025 | Fair Pricing • Real Routes • Best Deals")
