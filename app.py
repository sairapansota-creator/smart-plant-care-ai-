
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import database

from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

def generate_pdf_report(plant_name, report_data, summary):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    content = []

    content.append(
        Paragraph("Smart Plant Care AI", styles["Title"])
    )
    content.append(
        Paragraph(f"Sensor Report: {plant_name}", styles["Heading2"])
    )
    content.append(
        Paragraph(
            f"Generated: {datetime.now():%d %b %Y, %I:%M %p}",
            styles["Normal"]
        )
    )
    content.append(Spacer(1, 16))

    summary_rows = [["Metric", "Average", "Minimum", "Maximum"]]

    for column, label in [
        ("Soil Moisture (%)", "Soil Moisture (%)"),
        ("Temperature (°C)", "Temperature (°C)"),
        ("Humidity (%)", "Humidity (%)"),
        ("Light Intensity (lux)", "Light Intensity (lux)")
    ]:
        if column in summary.columns:
            summary_rows.append([
                label,
                str(summary.loc["Average", column]),
                str(summary.loc["Minimum", column]),
                str(summary.loc["Maximum", column])
            ])

    content.append(
        Paragraph("Sensor Summary", styles["Heading2"])
    )

    summary_table = Table(summary_rows, repeatRows=1)
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (1, 1), (-1, -1), "CENTER")
    ]))
    content.append(summary_table)
    content.append(Spacer(1, 16))

    content.append(
        Paragraph("Sensor Reading History", styles["Heading2"])
    )

    columns = [
        ("recorded_at", "Recorded At"),
        ("soil_moisture", "Soil Moisture (%)"),
        ("temperature", "Temperature (°C)"),
        ("humidity", "Humidity (%)"),
        ("light_intensity", "Light (lux)")
    ]

    table_data = [[label for _, label in columns]]

    for _, row in report_data.iterrows():
        values = []
        for key, _ in columns:
            value = row.get(key)

            if pd.isna(value):
                values.append("N/A")
            elif key == "recorded_at":
                values.append(str(value))
            else:
                values.append(str(round(float(value), 2)))

        table_data.append(values)

    history_table = Table(
        table_data,
        repeatRows=1,
        colWidths=[150, 110, 110, 100, 100]
    )
    history_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP")
    ]))

    content.append(history_table)
    content.append(Spacer(1, 12))
    content.append(
        Paragraph(
            "Note: Demo readings are simulated and are not real sensor measurements.",
            styles["Italic"]
        )
    )

    document.build(content)
    buffer.seek(0)
    return buffer.getvalue()

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
        "Reports",
        "Plant Care Recommendations"
    ]
)


if page == "Dashboard":
    st.title("Smart Plant Care AI")
    st.subheader("Plant Health Dashboard")

    database.initialize_database()
    plants = database.get_plants()

    if not plants:
        st.info(
            "No plants found. Please add a plant in Plant Profiles first."
        )
    else:
        plant_options = {
            f"{plant['name']} (ID: {plant['id']})": plant["id"]
            for plant in plants
        }

        selected_plant = st.selectbox(
            "Select Plant",
            list(plant_options.keys()),
            key="dashboard_plant"
        )

        plant_id = plant_options[selected_plant]
        readings = database.get_sensor_readings(plant_id, limit=100)

        if not readings:
            st.info(
                "No saved sensor readings found for this plant. "
                "Open IoT Monitoring and save a demo reading first."
            )
        else:
            data = pd.DataFrame(readings)
            data["recorded_at"] = pd.to_datetime(
                data["recorded_at"], errors="coerce"
            )
            data = data.sort_values("recorded_at")

            latest = data.iloc[-1]

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Soil Moisture",
                f"{latest['soil_moisture']:.1f}%"
                if pd.notna(latest["soil_moisture"]) else "N/A"
            )

            col2.metric(
                "Temperature",
                f"{latest['temperature']:.1f} °C"
                if pd.notna(latest["temperature"]) else "N/A"
            )

            col3.metric(
                "Humidity",
                f"{latest['humidity']:.1f}%"
                if pd.notna(latest["humidity"]) else "N/A"
            )

            col4.metric(
                "Light Intensity",
                f"{latest['light_intensity']:.0f} lux"
                if pd.notna(latest["light_intensity"]) else "N/A"
            )

            st.caption(
                "Values shown are the latest saved readings. "
                "If you are using demo data, these are not real sensor measurements."
            )

            st.subheader("Sensor History")

            chart_data = data[
                [
                    "recorded_at",
                    "soil_moisture",
                    "temperature",
                    "humidity"
                ]
            ].rename(
                columns={
                    "recorded_at": "Time",
                    "soil_moisture": "Soil Moisture (%)",
                    "temperature": "Temperature (°C)",
                    "humidity": "Humidity (%)"
                }
            )

            chart_data = chart_data.dropna(
                subset=["Time"]
            )

            if not chart_data.empty:
                fig = px.line(
                    chart_data,
                    x="Time",
                    y=[
                        "Soil Moisture (%)",
                        "Temperature (°C)",
                        "Humidity (%)"
                    ],
                    markers=True,
                    title="Saved Sensor Readings"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            st.subheader("Plant Care Alerts")

            moisture = latest["soil_moisture"]

            if pd.notna(moisture) and moisture < 30:
                st.warning(
                    "Soil moisture is low. Check the soil near the roots "
                    "before deciding whether to water."
                )
            elif pd.notna(moisture) and moisture > 80:
                st.warning(
                    "Soil moisture is high. Check drainage and avoid "
                    "watering again until the soil condition is assessed."
                )
            elif pd.notna(moisture):
                st.success(
                    "No moisture alert based on the configured demo threshold."
                )
            else:
                st.info("Soil moisture data is unavailable.")

            st.subheader("Recent Sensor Records")

            display_data = data.sort_values(
                "recorded_at", ascending=False
            ).head(10)

            st.dataframe(
                display_data,
                use_container_width=True,
                hide_index=True
            )


elif page == "Plant Profiles":

    st.subheader("🌿 Plant Profiles")
    st.write("Apne plants ko database mein permanently save karein.")

    # Database initialize karein
    database.initialize_database()

    # New plant form
    with st.form("plant_profile_form"):
        st.subheader("Add New Plant")

        plant_name = st.text_input(
            "Plant Name",
            placeholder="e.g. My Money Plant"
        )

        species = st.selectbox(
            "Plant Type",
            [
                "Tomato",
                "Rose",
                "Money Plant",
                "Basil",
                "Other"
            ]
        )

        pot_size = st.selectbox(
            "Pot Size",
            ["Small", "Medium", "Large"]
        )

        submitted = st.form_submit_button("Save Plant")

        if submitted:
            if plant_name.strip():
                try:
                    plant_id = database.add_plant(
                        plant_name.strip(),
                        species,
                        pot_size
                    )

                    st.success(
                        f"Plant successfully saved! Plant ID: {plant_id}"
                    )

                except Exception as error:
                    st.error(f"Plant save nahi hua: {error}")

            else:
                st.warning("Please plant ka naam enter karein.")

    st.divider()

    # Saved plants display karein
    st.subheader("🌱 Saved Plants")

    try:
        plants = database.get_plants()

        if plants:
            plants_df = pd.DataFrame(plants)

            st.dataframe(
                plants_df,
                use_container_width=True,
                hide_index=True
            )

            st.success(f"Database mein {len(plants)} plant(s) saved hain.")

        else:
            st.info("Abhi koi plant save nahi hua. Upar form fill karein.")

    except Exception as error:
        st.error(f"Plants load nahi ho sake: {error}")



elif page == "AI Plant Doctor":
    st.subheader("AI Plant Doctor")

    st.write(
        "Upload a plant leaf image and select the symptoms "
        "to receive preliminary plant care guidance."
    )

    uploaded_image = st.file_uploader(
        "Upload a Plant Leaf Image",
        type=["jpg", "jpeg", "png"]
    )

    plant_type = st.selectbox(
        "Select Plant Type",
        [
            "Tomato",
            "Rose",
            "Money Plant",
            "Basil",
            "Other"
        ],
        key="doctor_plant_type"
    )

    symptoms = st.multiselect(
        "Select Plant Symptoms",
        [
            "Yellow leaves",
            "Brown spots",
            "White powder on leaves",
            "Wilting leaves",
            "Holes in leaves",
            "Slow growth",
            "No visible symptoms"
        ]
    )

    soil_condition = st.selectbox(
        "Soil Condition",
        [
            "Not sure",
            "Dry",
            "Slightly moist",
            "Wet"
        ]
    )

    if uploaded_image:
        st.image(
            uploaded_image,
            caption="Uploaded Plant Leaf",
            use_container_width=True
        )

    if st.button("Analyze Plant Condition"):
        st.subheader("Initial Plant Care Guidance")

        guidance = []

        if "Yellow leaves" in symptoms:
            guidance.append(
                "Yellow leaves may indicate watering issues, "
                "nutrient deficiencies, or natural leaf aging. "
                "Check the soil and drainage."
            )

        if "Brown spots" in symptoms:
            guidance.append(
                "Brown spots may have fungal, bacterial, "
                "environmental, or other causes. Inspect the leaves carefully."
            )

        if "White powder on leaves" in symptoms:
            guidance.append(
                "White powder may indicate a fungal infection. "
                "A proper diagnosis is needed to confirm the cause."
            )

        if "Wilting leaves" in symptoms:
            guidance.append(
                "Check soil moisture and drainage before watering. "
                "Wilting can result from both underwatering and overwatering."
            )

        if "Holes in leaves" in symptoms:
            guidance.append(
                "Inspect both sides of the leaves for insects "
                "or signs of chewing damage."
            )

        if "Slow growth" in symptoms:
            guidance.append(
                "Review light exposure, watering, pot size, "
                "and growing conditions."
            )

        if soil_condition == "Dry":
            guidance.append(
                "The soil is reported as dry. Check the root-zone "
                "moisture and the plant's watering needs."
            )
        elif soil_condition == "Wet":
            guidance.append(
                "The soil is reported as wet. Check drainage and "
                "allow excess water to drain before watering again."
            )

        if not symptoms and soil_condition == "Not sure":
            guidance.append(
                "Select visible symptoms or provide more information "
                "for more relevant guidance."
            )

        for item in guidance:
            st.write(f"- {item}")

        st.warning(
            "This is general symptom-based guidance. "
            "An AI disease detection model has not yet been integrated, "
            "so no confirmed diagnosis is provided."
        )


elif page == "IoT Monitoring":
    st.subheader("📡 IoT Device Monitoring")

    database.initialize_database()
    plants = database.get_plants()

    col1, col2 = st.columns(2)
    col1.metric("Connected Devices", "0")
    col2.metric("Data Source", "Demo Mode")

    st.info(
        "ESP32 abhi connect nahi hai. Neeche ki readings "
        "sirf testing ke liye hain, real sensor data nahi."
    )

    if not plants:
        st.warning(
            "Pehle Plant Profiles page par kam az kam ek plant save karein."
        )
    else:
        plant_options = {
            f"{plant['name']} (ID: {plant['id']})": plant["id"]
            for plant in plants
        }

        selected_plant = st.selectbox(
            "Plant select karein",
            list(plant_options.keys())
        )
        plant_id = plant_options[selected_plant]

        st.subheader("🧪 Demo Sensor Readings")

        col1, col2 = st.columns(2)

        with col1:
            soil = st.slider("Soil Moisture (%)", 0, 100, 42)
            temperature = st.slider(
                "Temperature (°C)", 0.0, 50.0, 26.4
            )

        with col2:
            humidity = st.slider("Humidity (%)", 0, 100, 48)
            light = st.number_input(
                "Light Intensity (lux)",
                min_value=0,
                max_value=100000,
                value=850
            )

        if st.button("Save Demo Reading"):
            database.save_sensor_reading(
                plant_id,
                soil,
                temperature,
                humidity,
                light
            )
            st.success(
                "Demo reading local database mein save ho gayi."
            )

        st.divider()
        st.subheader("📈 Saved Sensor History")

        readings = database.get_sensor_readings(plant_id)

        if readings:
            history_df = pd.DataFrame(readings)
            st.dataframe(
                history_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Is plant ki abhi koi sensor reading save nahi hui.")
       
elif page == "Plant Care Recommendations":
    st.subheader("🌱 Plant Care Recommendations")
    st.write(
        "Get care suggestions based on your latest saved sensor readings."
    )

    database.initialize_database()
    plants = database.get_plants()

    if not plants:
        st.info("Please add a plant in Plant Profiles first.")

    else:
        plant_options = {
            f"{plant['name']} (ID: {plant['id']})": plant["id"]
            for plant in plants
        }

        selected_plant = st.selectbox(
            "Select Plant",
            list(plant_options.keys()),
            key="care_plant"
        )

        plant_id = plant_options[selected_plant]

        readings = database.get_sensor_readings(
            plant_id,
            limit=1
        )

        if not readings:
            st.info(
                "No sensor readings found. "
                "Save a reading in IoT Monitoring first."
            )

        else:
            reading = readings[0]
            recommendations = []
            critical = False

            moisture = reading.get("soil_moisture")
            temperature = reading.get("temperature")
            humidity = reading.get("humidity")
            light = reading.get("light_intensity")

            st.subheader("Latest Sensor Readings")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Soil Moisture",
                f"{moisture}%" if moisture is not None else "N/A"
            )
            col2.metric(
                "Temperature",
                f"{temperature} °C"
                if temperature is not None else "N/A"
            )
            col3.metric(
                "Humidity",
                f"{humidity}%"
                if humidity is not None else "N/A"
            )
            col4.metric(
                "Light Intensity",
                f"{light} lux" if light is not None else "N/A"
            )

            if moisture is not None:
                if moisture < 30:
                    recommendations.append(
                        "Soil moisture is low. Check the soil and "
                        "water the plant if the soil is dry."
                    )
                    critical = True
                elif moisture > 80:
                    recommendations.append(
                        "Soil moisture is high. Avoid watering until "
                        "the soil has been checked."
                    )
                else:
                    recommendations.append(
                        "Soil moisture is within the app's general "
                        "target range."
                    )

            if temperature is not None:
                if temperature < 10:
                    recommendations.append(
                        "Temperature is low. Protect the plant from cold."
                    )
                    critical = True
                elif temperature > 35:
                    recommendations.append(
                        "Temperature is high. Reduce heat exposure "
                        "and check the plant for stress."
                    )
                    critical = True
                elif temperature > 30:
                    recommendations.append(
                        "Temperature is warm. Monitor the plant for "
                        "heat stress."
                    )
                else:
                    recommendations.append(
                        "Temperature is within the app's general "
                        "target range."
                    )

            if humidity is not None:
                if humidity < 30:
                    recommendations.append(
                        "Air humidity is low. Check the needs of "
                        "your plant species."
                    )
                elif humidity > 80:
                    recommendations.append(
                        "Air humidity is high. Ensure suitable airflow "
                        "and monitor for fungal problems."
                    )
                else:
                    recommendations.append(
                        "Air humidity is within the app's general "
                        "target range."
                    )

            if light is not None:
                if light < 1000:
                    recommendations.append(
                        "Light level is low. Check whether your plant "
                        "needs a brighter location."
                    )
                elif light > 20000:
                    recommendations.append(
                        "Light level is high. Check whether direct "
                        "sunlight may harm your plant."
                    )
                else:
                    recommendations.append(
                        "Light level is within the app's general "
                        "target range."
                    )

            st.subheader("Plant Status")

            if critical:
                st.warning(
                    "Needs Attention — review the recommendations below."
                )
            else:
                st.success(
                    "No critical threshold detected by the app. "
                    "Continue monitoring your plant."
                )

            st.subheader("Care Recommendations")

            for item in recommendations:
                st.markdown(f"- {item}")

            st.subheader("Plant Species-Based Care")

            selected_plant_data = next(
                plant for plant in plants
                if plant["id"] == plant_id
            )

            species = str(
                selected_plant_data.get("species") or ""
            ).strip().lower()

            species_advice = {
                "snake plant": [
                    "Allow the soil to dry out between waterings.",
                    "Bright indirect light is suitable; it can tolerate lower light.",
                    "Avoid waterlogging to help prevent root rot."
                ],
                "money plant": [
                    "Bright, indirect light is generally suitable.",
                    "Water when the upper soil layer begins to dry.",
                    "Avoid leaving the roots in standing water."
                ],
                "pothos": [
                    "Provide bright, indirect light for good growth.",
                    "Water when the upper soil layer begins to dry.",
                    "Avoid waterlogging the pot."
                ],
                "rose": [
                    "Provide several hours of suitable sunlight daily.",
                    "Water the soil when needed while ensuring good drainage.",
                    "Monitor for pests and remove dead leaves."
                ],
                "peace lily": [
                    "Provide bright, indirect light.",
                    "Keep the soil lightly moist, but not waterlogged.",
                    "Monitor humidity and leaf condition."
                ],
                "aloe vera": [
                    "Provide bright light, with gradual adjustment to direct sun.",
                    "Let the soil dry completely between waterings.",
                    "Use a well-draining potting mix."
                ],
                "tomato": [
                    "Provide ample sunlight, typically around 6–8 hours daily.",
                    "Keep soil moisture consistent without waterlogging.",
                    "Monitor leaves and stems for pests or disease."
                ]
            }

            if species in species_advice:
                st.write(f"Care tips for: {species.title()}")

                for tip in species_advice[species]:
                    st.markdown(f"- {tip}")

            elif not species:
                st.info(
                    "Plant species is not recorded. "
                    "Add its species in Plant Profiles for tailored tips."
                )

            else:
                st.info(
                    f"No specific tips configured for '{species}'. "
                    "Showing general sensor-based recommendations above."
                )

            st.caption(
                "These are general threshold-based suggestions, not "
                "a diagnosis. Ideal conditions vary by plant species. "
                "Sensor readings may be simulated demo data."
            )

elif page == "Reports":
    st.subheader("Plant Sensor Reports")

    database.initialize_database()
    plants = database.get_plants()

    if not plants:
        st.info(
            "No plants found. Please add a plant in Plant Profiles first."
        )
    else:
        plant_options = {
            f"{plant['name']} (ID: {plant['id']})": plant["id"]
            for plant in plants
        }

        selected_plant = st.selectbox(
            "Select Plant",
            list(plant_options.keys()),
            key="reports_plant"
        )

        plant_id = plant_options[selected_plant]

        readings = database.get_sensor_readings(
            plant_id,
            limit=1000
        )

        if not readings:
            st.info(
                "No sensor readings available. "
                "Save readings from IoT Monitoring first."
            )
        else:
            report_data = pd.DataFrame(readings)
            readings_df = report_data.copy()

            report_data = report_data.rename(
                columns={
                    "id": "Reading ID",
                    "plant_id": "Plant ID",
                    "soil_moisture": "Soil Moisture (%)",
                    "temperature": "Temperature (°C)",
                    "humidity": "Humidity (%)",
                    "light_intensity": "Light Intensity (lux)",
                    "recorded_at": "Recorded At"
                }
            )

            st.success(
                f"{len(report_data)} saved reading(s) found."
            )

            st.subheader("Sensor Reading History")

            st.dataframe(
                report_data,
                use_container_width=True,
                hide_index=True
            )

            st.subheader("Summary Statistics")

            numeric_columns = [
                "Soil Moisture (%)",
                "Temperature (°C)",
                "Humidity (%)",
                "Light Intensity (lux)"
            ]

            available_columns = [
                column for column in numeric_columns
                if column in report_data.columns
            ]

            if available_columns:
                summary = report_data[available_columns].agg(
                    ["mean", "min", "max"]
                ).round(2)

                summary.index = ["Average", "Minimum", "Maximum"]

                st.dataframe(
                    summary,
                    use_container_width=True
                )

            csv_data = report_data.to_csv(
                index=False
            ).encode("utf-8-sig")

            st.download_button(
                label="Download CSV Report",
                data=csv_data,
                file_name=f"plant_sensor_report_{plant_id}.csv",
                mime="text/csv"
            )

            st.caption(
                "Report generated from saved database readings. "
                "Demo readings are simulated and are not real sensor measurements."
            )
            
            pdf_summary = report_data[available_columns].agg(
                ["mean", "min", "max"]
            ).round(2)

            pdf_summary.index = [
                "Average",
                "Minimum",
                "Maximum"
            ]

            selected_plant_name = next(
                plant["name"]
                for plant in plants
                if plant["id"] == plant_id
            )

            pdf_bytes = generate_pdf_report(
                selected_plant_name,
                readings_df,
                pdf_summary
            )

            st.download_button(
                label="Download PDF Report",
                data=pdf_bytes,
                file_name=f"plant_sensor_report_{plant_id}.pdf",
                mime="application/pdf"
            )