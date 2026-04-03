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

# ================= SIDEBAR =================
menu = st.sidebar.selectbox("MENU", ["Home", "About"])

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
}
</style>
""", unsafe_allow_html=True)

# ================= HOME PAGE =================
if menu == "Home":

    st.markdown("<h1>✈️ Flight Price Prediction System</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#ddd;text-align:center;'>Enter flight details to predict ticket pricestreamlit</p>", unsafe_allow_html=True)

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

    # Prediction Logic
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

    # Predict Button
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

        st.success(f"💰 Estimated Flight Price: ₹ {price}")

    # History
    st.subheader("📊 Prediction History")
    df = pd.read_sql("SELECT * FROM flight_predictions ORDER BY id DESC", conn)
    st.dataframe(df)

    # Pie Chart
    st.subheader("✈️ Airline-wise Distribution")

    if not df.empty:
        airline_count = df["airline"].value_counts()
        fig, ax = plt.subplots()
        ax.pie(airline_count.values, labels=airline_count.index, autopct="%1.1f%%")
        ax.axis("equal")
        st.pyplot(fig)
    else:
        st.info("No data available")

    # Clear Database
    if st.button("❌ Clear All Records"):
        cursor.execute("DELETE FROM flight_predictions")
        conn.commit()
        st.success("All records cleared!")
        st.rerun()

# ================= ABOUT PAGE =================
elif menu == "About":

    st.markdown("<h1 >📘 About Project</h1>",
    unsafe_allow_html=True
)
    st.markdown("""
    <div style='color:white;'>

### ✈️ Flight Price Prediction System

The Flight Price Prediction System is a Machine Learning–based web application
developed to estimate flight ticket prices based on user inputs such as source,
destination, journey date, duration, and number of stops. The primary objective
of this project is to demonstrate the practical application of data science,
machine learning, and web development within the travel and airline industry.
By leveraging predictive models, the system provides accurate, data-driven
price estimates, enabling users to make informed and cost-effective decisions.

### 🎯 Objective
- To analyze historical flight data and identify factors affecting ticket prices
- To build an efficient machine learning model for price prediction
- To provide a user-friendly interface for easy interaction
- To help users find the best time to book flights 

### 🚀 Features
- Easy interface
- Fast prediction
- Data storage
- Graph visualization

### 🛠️ Technologies
- Python
- Streamlit
- SQLite
- Pandas, Matplotlib

### ✅ Conclusion
The Flight Price Prediction System is an intelligent and practical solution that simplifies travel planning
It enables users to make better decisions by providing reliable and timely price predictions.

### 👩‍💻 Developed By
Pragti Singh  
MCA Student  

</div>
""", unsafe_allow_html=True)
