#!/usr/bin/env python3
# ============================================================================
# RIDESHARE CARPOOL - BEAUTIFUL UI VERSION
# ============================================================================
# Design inspired by modern carpool apps
# Features: Professional header, search bar, filter tabs, beautiful cards
# ============================================================================

import streamlit as st
import pandas as pd
import pickle
import folium
from streamlit_folium import st_folium
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
# CUSTOM CSS - BEAUTIFUL STYLING
# ============================================================================

st.markdown("""
    <style>
        * {
            margin: 0;
            padding: 0;
        }

        body {
            background-color: #f5f7fa;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        /* WELCOME HEADER */
        .welcome-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem 2rem;
            margin: -3rem -1.5rem 2rem -1.5rem;
            border-radius: 0 0 20px 20px;
        }

        .welcome-section h1 {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .welcome-section p {
            font-size: 15px;
            opacity: 0.95;
            line-height: 1.6;
            margin-bottom: 1rem;
        }

        .stats-row {
            display: flex;
            gap: 2rem;
            margin-top: 1rem;
            font-size: 14px;
        }

        /* SEARCH CONTAINER */
        .search-box {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            margin-bottom: 2rem;
        }

        /* FILTER TABS */
        .filter-tabs {
            display: flex;
            gap: 1.5rem;
            margin-bottom: 2rem;
            border-bottom: 2px solid #e8ecf1;
            padding-bottom: 1rem;
        }

        .filter-tab {
            font-size: 15px;
            color: #95a3b3;
            cursor: pointer;
            padding-bottom: 8px;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }

        .filter-tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
            font-weight: 600;
        }

        /* RIDE CARD */
        .ride-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            transition: all 0.3s ease;
            border: 1px solid #f0f3f7;
            margin-bottom: 1rem;
        }

        .ride-card:hover {
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
            transform: translateY(-4px);
        }

        /* MAP SECTION */
        .map-section {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            margin-bottom: 2rem;
        }

        .info-badge {
            display: inline-block;
            background: #f0f2f6;
            color: #667eea;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            margin: 0.5rem 0.5rem 0.5rem 0;
        }
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
    st.session_state.active_tab = "All Rides"

# ============================================================================
# LOAD DATA
# ============================================================================

@st.cache_resource
def generate_owners(n):
    first_names = ['Aarav', 'Aditya', 'Arjun', 'Aryan', 'Ashok', 'Amit', 'Anand', 'Atul',
                   'Bhuvan', 'Bhavesh', 'Chirag', 'Chetan', 'Deepak', 'Devendra', 'Dhruv',
                   'Farhan', 'Fahim', 'Gaurav', 'Girish', 'Harsh', 'Harish', 'Ishan',
                   'Jayesh', 'Jayadev', 'Karan', 'Krishan', 'Lalit', 'Mahesh', 'Manish',
                   'Mohan', 'Naveen', 'Nilesh', 'Nikhil', 'Omkar', 'Pankaj', 'Prakash',
                   'Rahul', 'Rajesh', 'Ravi', 'Sandeep', 'Suresh', 'Sanjay', 'Tarun',
                   'Tushar', 'Varun', 'Vikram', 'Vikas', 'Vinay', 'Vivek', 'Wasim', 'Yash'] * 160

    surnames = ['Singh', 'Kumar', 'Sharma', 'Patel', 'Gupta', 'Verma', 'Pandey', 'Mishra',
                'Desai', 'Rao', 'Reddy', 'Roy', 'Ghosh', 'Dutta', 'Banerjee', 'Bhattacharya',
                'Mukherjee', 'Das', 'Nair', 'Menon', 'Iyer', 'Iyengar', 'Krishnan', 'Pillay',
                'Srivastava', 'Jain', 'Malhotra', 'Kapoor', 'Grover', 'Ahuja', 'Chopra',
                'Khanna', 'Bhatia', 'Mittal', 'Saxena', 'Mehra', 'Kohli', 'Sethi', 'Talwar',
                'Sinha', 'Bose', 'Dey', 'Chattopadhyay', 'Sen', 'Dasgupta', 'Nag', 'Bagchi',
                'Mitra', 'Sarkar', 'Chatterjee', 'Basu', 'Saha'] * 160

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
    df = pd.read_csv("car-data.csv")
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

def calc_fare(distance):
    base = 50
    if distance <= 50: per_km = 3.5
    elif distance <= 150: per_km = 3.0
    elif distance <= 300: per_km = 2.5
    else: per_km = 2.0
    return int(base + distance * per_km)

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
    <div class="welcome-section">
        <h1>👋 Welcome back, User!</h1>
        <p>Share rides, save money, and reduce your carbon footprint. Connect with travelers heading your way.</p>
        <div class="stats-row">
            <div>👥 10,000+ Active Users</div>
            <div>💰 Save up to 70%</div>
            <div>🌍 Eco-Friendly</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ============================================================================
# SEARCH BOX
# ============================================================================

st.markdown('<div class="search-box">', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([2, 2, 2, 1.2])

with col1:
    pickup = st.selectbox("From (City)", sorted(df['pickup location'].unique()), label_visibility="collapsed", key="p1")

with col2:
    drop = st.selectbox("To (City)", sorted(df['drop location'].unique()), label_visibility="collapsed", key="p2")

with col3:
    date = st.date_input("Select date", label_visibility="collapsed", key="p3")

with col4:
    if st.button("🔍 Search Rides", use_container_width=True):
        st.session_state.show_results = True
        st.session_state.pickup = pickup
        st.session_state.drop = drop
        st.session_state.date = date

        if pickup in coords and drop in coords:
            lat1, lon1 = coords[pickup]
            lat2, lon2 = coords[drop]
            st.session_state.distance = calc_distance(lat1, lon1, lat2, lon2)
        else:
            st.session_state.distance = 150

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# FILTER TABS
# ============================================================================

if st.session_state.show_results:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("All Rides", use_container_width=True):
            st.session_state.active_tab = "All Rides"
    with col2:
        if st.button("Today", use_container_width=True):
            st.session_state.active_tab = "Today"
    with col3:
        if st.button("Upcoming", use_container_width=True):
            st.session_state.active_tab = "Upcoming"

# ============================================================================
# RESULTS - TWO COLUMN LAYOUT
# ============================================================================

if st.session_state.show_results:
    # Two-column layout for map and rides
    col_map, col_rides = st.columns([2, 1])

    # ===== LEFT: MAP =====
    with col_map:
        st.markdown('<div class="map-section">', unsafe_allow_html=True)
        st.write("### 🗺️ Route")

        if st.session_state.pickup in coords and st.session_state.drop in coords:
            lat1, lon1 = coords[st.session_state.pickup]
            lat2, lon2 = coords[st.session_state.drop]

            center_lat = (lat1 + lat2) / 2
            center_lon = (lon1 + lon2) / 2

            m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="OpenStreetMap")

            # Markers
            folium.Marker([lat1, lon1], popup="🟢 Start", icon=folium.Icon(color='green')).add_to(m)
            folium.Marker([lat2, lon2], popup="🔴 End", icon=folium.Icon(color='red')).add_to(m)

            # Blue line
            folium.PolyLine([[lat1, lon1], [lat2, lon2]], color='blue', weight=4, opacity=0.8, dash_array='5,5').add_to(m)

            # Circles
            folium.CircleMarker([lat1, lon1], radius=8, color='green', fill=True, fillColor='lightgreen', weight=3).add_to(m)
            folium.CircleMarker([lat2, lon2], radius=8, color='red', fill=True, fillColor='lightcoral', weight=3).add_to(m)

            st_folium(m, use_container_width=True, height=600)

            # ROUTE DETAILS - STREAMLIT NATIVE (NO HTML)
            st.write("### 📍 Route Details:")
            st.write(f"🟢 **{st.session_state.pickup}**")
            st.caption(f"({lat1:.4f}, {lon1:.4f})")

            st.write("")  # Spacing

            st.write(f"🔴 **{st.session_state.drop}**")
            st.caption(f"({lat2:.4f}, {lon2:.4f})")

            st.write("")  # Spacing
        else:
            # Fallback map when coordinates are missing
            m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles="OpenStreetMap")
            st.info("Showing default map because coordinates for the selected cities were not found.")
            st_folium(m, use_container_width=True, height=600)

            # ROUTE DETAILS - STREAMLIT NATIVE (NO HTML)
            st.write("### 📍 Route Details:")
            st.write(f"🟢 **{st.session_state.pickup}**")
            st.caption("(coordinates unavailable)")

            st.write("")  # Spacing

            st.write(f"🔴 **{st.session_state.drop}**")
            st.caption("(coordinates unavailable)")

            st.write("")  # Spacing

            st.warning("Coordinates not available; showing default map.")

        st.divider()

        # Info badges
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("📏 Distance", f"{st.session_state.distance} km")
        with col_b:
            st.metric("📅 Date", st.session_state.date.strftime("%d %b"))
        st.markdown('</div>', unsafe_allow_html=True)

    # ===== RIGHT: RIDE CARDS =====
    with col_rides:
        st.write("### 🚗 Available Rides")

        route_data = df[(df['pickup location'] == st.session_state.pickup) & 
                        (df['drop location'] == st.session_state.drop)]

        if len(route_data) == 0:
            route_data = df[df['pickup location'] == st.session_state.pickup].head(6)

        if len(route_data) > 0:
            for idx, (_, ride) in enumerate(route_data.head(6).iterrows()):
                with st.container():
                    st.markdown('<div class="ride-card">', unsafe_allow_html=True)

                    # Top row - Owner info
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        owner_initial = ride['Owner_Name'][0].upper()
                        st.markdown(f"**{owner_initial}** {ride['Owner_Name']} | ⭐ {ride['Rating']}")
                    with col_b:
                        st.markdown(f"👥 {ride['seats']}")

                    # Route
                    st.markdown(f"📍 **From:** {st.session_state.pickup}")
                    st.markdown(f"📍 **To:** {st.session_state.drop}")

                    # Time
                    st.markdown(f"📅 {st.session_state.date.strftime('%b %d, %Y')} | ⏰ {ride['Availability']} AM")

                    # Bottom - Price and button
                    fare = calc_fare(st.session_state.distance)
                    col_x, col_y = st.columns([2, 1])
                    with col_x:
                        st.markdown(f"## 🟢 **₹{fare}** per seat")
                    with col_y:
                        st.button("View", key=f"v_{idx}", use_container_width=True)

                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("No rides available for this route")

else:
    st.info("🔍 Search for rides to see available options")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("<p style='text-align: center; color: #95a3b3; font-size: 13px;'>🚗 RideShare © 2025 | Save up to 70% on commute costs</p>", unsafe_allow_html=True)
