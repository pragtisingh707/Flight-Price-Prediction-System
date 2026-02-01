
import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Flight Price Prediction System",
    page_icon="✈️",
    layout="centered"
)

# ================= DATABASE CONNECTION =================
conn = sqlite3.connect("flight_price.db", check_same_thread=False)
cursor = conn.cursor()

# ================= CREATE TABLE =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS flight_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    airline TEXT,
    source TEXT,
    destination TEXT,
    stops TEXT,
    journey_date TEXT,
    departure_time TEXT,
    predicted_price REAL
)
""")
conn.commit()

# ================= CLEAR DATABASE FUNCTION (MUST EXIST) =================
def clear_database():
    cursor.execute("DELETE FROM flight_predictions")
    conn.commit()

# ================= CSS =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #141e30, #243b55);
            color: orange;
}

h1 {
    color: white;
    text-align: center;
    font-weight: 800;
}

label {
    color: white !important;
    font-weight: 600;
}

button {
    width: 100%;
    font-size: 18px;
    border-radius: 12px;
}

.result {
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    padding: 15px;
    border-radius: 12px;
    color: black;
    text-align: center;
    font-size: 22px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ================= TITLE =================
st.markdown("<h1>✈️ Flight Price Prediction System</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#ddd;text-align:center;font-size:28px;'>Enter flight details to predict ticket price</p>", unsafe_allow_html=True)

# ================= INPUT =================
col1, col2 = st.columns(2)

with col1:
    airline = st.selectbox("Airline", ['IndiGo', 'Air India', 'Jet Airways', 'SpiceJet',
     'Vistara', 'GoAir', 'Multiple carriers'])
    source = st.selectbox("Source City", ["Delhi", "Mumbai", "Kolkata", "Chennai", 'Banglore'])
    journey_date = st.date_input("Journey Date", min_value=date.today())

with col2:
    destination = st.selectbox("Destination City", ["Cochin", "Delhi", "Hyderabad", "Kolkata","Banglore"])
    stops = st.selectbox("Total Stops", ["non-stop", "1 stop", "2 stops",'3 stops', '4 stops'])
    dep_time = st.time_input("Departure Time")

# ================= PREDICTION LOGIC =================
def predict_price(airline, stops):
    base_price = 3500

    airline_factor = {
        "IndiGo": 1.0,
        "Air India": 1.2,
        'Jet Airways':1.1,
        "SpiceJet": 0.9,
        "Vistara": 1.4,
        "GoAir":0.8, 
        'Multiple carriers':0.7
    }

    stop_factor = {
        "non-stop": 1.4,
        "1 stop": 1.1,
        "2 stops": 0.9,
        '3 stops':0.8,
        '4 stops':0.7
    }

    return round(base_price * airline_factor[airline] * stop_factor[stops], 2)

# ================= PREDICT BUTTON =================
if st.button("🚀 Predict Price"):
    price = predict_price(airline, stops)

    cursor.execute("""
    INSERT INTO flight_predictions
    (airline, source, destination, stops, journey_date, departure_time, predicted_price)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        airline,
        source,
        destination,
        stops,
        journey_date.strftime("%Y-%m-%d"),
        dep_time.strftime("%H:%M"),
        price
    ))
    conn.commit()

    st.markdown(f"<div class='result'>💰 Estimated Flight Price: ₹ {price}</div>", unsafe_allow_html=True)

# ================= HISTORY =================
st.subheader("📊 Prediction History")
df = pd.read_sql("SELECT * FROM flight_predictions ORDER BY id DESC", conn)
st.dataframe(df)

# ================= PIE CHART =================
st.subheader("✈️ Airline-wise Prediction Distribution")

if not df.empty:
    airline_count = df["airline"].value_counts()

    color_map = {
        
        "IndiGo": "#1f77b4",            # Blue
        "Air India": "#2ca02c",         # Green
        "SpiceJet": "#ff7f0e",          # Orange
        "Vistara": "#9467bd",           # Purple
        "Jet Airways": "#d62728",       # Red
        "GoAir": "#17becf",             # Cyan
        "Multiple carriers": "#bcbd22"  # Olive
    }

    colors = [color_map.get(a, "#cccccc") for a in airline_count.index]

    fig, ax = plt.subplots()
    ax.pie(
        airline_count.values,
        labels=airline_count.index,
        colors=colors,
        autopct="%1.1f%%",
        startangle=90
    )
    ax.axis("equal")
    st.pyplot(fig)
else:
    st.info("No data available for pie chart")

# ================= CLEAR DATABASE =================
st.subheader("🗑️ Database Control")

if st.button("❌Clear All Records"):
    cursor.execute("DELETE FROM flight_predictions")
    conn.commit()
    st.success("All records cleared successfully!")
    st.rerun()   # ✅ correct function
