import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Smart Plant Care AI",
    page_icon="🌱",
    layout="wide"
)

# Demo data: hardware baad mein connect hoga
st.title("🌱 Smart Plant Care AI")
st.markdown("### Intelligent Plant Monitoring & Care Assistant")

st.info(
    "🧪 DEMO MODE: Abhi simulated sensor readings hain. "
    "ESP32 hardware baad mein connect hoga."
)

# Sidebar
st.sidebar.title("🌿 Navigation")
page = st.sidebar.radio(
    "Select Module",
    [
        "Dashboard",
        "Plant Profiles",
        "AI Plant Doctor",
        "IoT Monitoring",
        "Reports"
    ]
)

if page == "Dashboard":
    st.subheader("Plant Health Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Soil Moisture", "42%", "2%")
    col2.metric("Temperature", "26.4 °C", "-0.6 °C")
    col3.metric("Humidity", "48%", "3%")
    col4.metric("Light Intensity", "850 lux", "50 lux")

    st.subheader("📊 Sensor History")

    times = [
        datetime.now() - timedelta(hours=i)
        for i in range(5, -1, -1)
    ]

    data = pd.DataFrame({
        "Time": times,
        "Soil Moisture (%)": [55, 52, 50, 47, 44, 42],
        "Temperature (°C)": [24, 24.5, 25, 25.5, 26, 26.4],
        "Humidity (%)": [55, 53, 52, 50, 49, 48],
    })

    fig = px.line(
        data,
        x="Time",
        y=[
            "Soil Moisture (%)",
            "Temperature (°C)",
            "Humidity (%)"
        ],
        markers=True,
        title="Simulated Sensor Readings"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🌱 Plant Care Alerts")
    st.warning(
        "Demo alert: Soil moisture ko check karein. "
        "Sirf is simulated reading ki bunyaad par pani na dein."
    )

    st.caption(
        f"Dashboard opened: {datetime.now():%d %b %Y, %I:%M %p}"
    )

elif page == "Plant Profiles":
    st.subheader("🌿 Plant Profiles")

    plant_name = st.text_input("Plant Name", "My Green Plant")
    species = st.selectbox(
        "Plant Type",
        ["Tomato", "Rose", "Money Plant", "Basil", "Other"]
    )
    pot_size = st.selectbox(
        "Pot Size",
        ["Small", "Medium", "Large"]
    )

    if st.button("Save Demo Profile"):
        st.success(
            f"Demo profile created for {plant_name} ({species}), "
            f"pot size: {pot_size}."
        )
        st.caption("Abhi profile permanently database mein save nahi hoti.")

elif page == "AI Plant Doctor":
    st.subheader("🩺 AI Plant Doctor")
    st.write(
        "Yahan hum baad mein leaf disease detection model "
        "aur proper AI agent integrate karenge."
    )

    uploaded_image = st.file_uploader(
        "Upload a plant leaf image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_image:
        st.image(
            uploaded_image,
            caption="Uploaded leaf image",
            use_container_width=True
        )
        st.info(
            "Image upload successful. Disease analysis model "
            "abhi integrate nahi hua."
        )

elif page == "IoT Monitoring":
    st.subheader("📡 IoT Device Monitoring")

    st.metric("Connected Devices", "0")
    st.metric("Data Source", "Simulated")
    st.write("ESP32 device baad mein API ke zariye connect hoga.")

elif page == "Reports":
    st.subheader("📄 Sensor Reports")

    report_data = pd.DataFrame({
        "Time": ["09:00", "10:00", "11:00", "12:00"],
        "Soil Moisture (%)": [51, 49, 45, 42],
        "Temperature (°C)": [24, 25, 25.8, 26.4],
        "Humidity (%)": [55, 52, 50, 48],
    })

    st.dataframe(report_data, use_container_width=True)

    csv_data = report_data.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Demo Report (CSV)",
        data=csv_data,
        file_name="plant_sensor_report.csv",
        mime="text/csv"
    )

    st.caption(
        "Ye demo report hai. PDF reports aur database integration "
        "aglay development steps mein add honge."
    )