"""
Streamlit dashboard for fleet monitoring.
"""

import pandas as pd
import requests
import streamlit as st
import plotly.express as px
from streamlit_autorefresh import st_autorefresh


API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="IoT Fleet Stream Engine",
    page_icon="🚚",
    layout="wide"
)

with st.sidebar:

    st.subheader("⚙️ Dashboard")

    auto_refresh = st.toggle(
        "Auto Refresh",
        value=True
    )

    refresh_seconds = st.select_slider(
        "Refresh",
        options=[5, 10, 20, 30, 60],
        value=30
    )
    
    st.markdown("---")
    st.caption(
        "🚚 50 simulated vehicles"
    )

    st.caption(
        f"⏱ Refresh every {refresh_seconds}s"
    )


if auto_refresh:
    st_autorefresh(
        interval=refresh_seconds * 1000,
        key="fleet_refresh"
    )

st.title("🚚 IoT Fleet Stream Engine")

st.caption(
    "Real-time fleet monitoring powered by "
    "Redpanda, TimescaleDB and FastAPI. "
    f"Last refresh: {pd.Timestamp.now().strftime('%H:%M:%S')}"
)

@st.cache_data(ttl=5)
def load_telemetry() -> pd.DataFrame:
    """
    Retrieve telemetry data from FastAPI.
    """

    response = requests.get(
        f"{API_URL}/api/telemetry?limit=500"
    )

    response.raise_for_status()

    return pd.DataFrame(response.json())


@st.cache_data(ttl=5)
def load_alerts() -> pd.DataFrame:
    """
    Retrieve alerts from FastAPI.
    """

    response = requests.get(
        f"{API_URL}/api/alerts?limit=50"
    )

    response.raise_for_status()

    return pd.DataFrame(response.json())

telemetry_df = load_telemetry()
alerts_df = load_alerts()

alert_count = len(alerts_df)    

alerts_df["timestamp"] = pd.to_datetime(
    alerts_df["timestamp"]
)

col1, col2, col3, col4 = st.columns(4)

active_vehicles = telemetry_df["vehicle_id"].nunique()

avg_temp = round(
    telemetry_df["temperature"].mean(),
    1
)

avg_fuel = round(
    telemetry_df["fuel_level"].mean(),
    1
)

col1.metric(
    "Active Vehicles",
    active_vehicles
)

col2.metric(
    "Recent Alerts",
    alert_count
)

col3.metric(
    "Avg Temperature",
    f"{avg_temp} °C"
)

col4.metric(
    "Avg Fuel",
    f"{avg_fuel} %"
)


st.subheader("🗺️ Fleet Position")

latest_positions = (
    telemetry_df
    .sort_values("timestamp")
    .groupby("vehicle_id")
    .tail(1)
)

fig_map = px.scatter_map(
    latest_positions,
    lat="latitude",
    lon="longitude",
    hover_name="vehicle_id",
    color="temperature",
    zoom=4,
    center={
        "lat": 46.603354,
        "lon": 1.888334
    }
)


st.plotly_chart(
    fig_map,
    use_container_width=True
)



selected_vehicle = st.selectbox(
    "Select Vehicle",
    sorted(
        telemetry_df["vehicle_id"].unique()
    )
)

st.subheader("🌡️ Temperature Evolution")

telemetry_df["timestamp"] = pd.to_datetime(
    telemetry_df["timestamp"]
)

vehicle_df = telemetry_df[
    telemetry_df["vehicle_id"] == selected_vehicle
]

vehicle_df = (
    vehicle_df
    .sort_values("timestamp")
    .tail(50)
)

fig_temp = px.line(
    vehicle_df.sort_values("timestamp"),
    x="timestamp",
    y="temperature",
    title=f"Temperature History - {selected_vehicle}"
)

st.plotly_chart(
    fig_temp,
    use_container_width=True
)

st.subheader("🚨 Latest Alerts")

if not alerts_df.empty:

    display_alerts = (
        alerts_df
        .sort_values(
            "timestamp",
            ascending=False
        )
        .head(20)
    )
    
    display_alerts = display_alerts[
        [
            "timestamp",
            "vehicle_id",
            "alert_type",
            "alert_value"
        ]
    ]
    
    display_alerts.columns = [
        "Timestamp",
        "Vehicle",
        "Alert Type",
        "Value"
    ]

    st.dataframe(
        display_alerts,
        use_container_width=True,
        hide_index=True
    )

else:
    st.success(
        "No alerts detected."
    )


st.divider()

if st.button(
    "⚠️ Inject Anomaly",
    type="primary"
):
    st.info(
        "Anomaly injection API will be added "
        "in the next step."
    )