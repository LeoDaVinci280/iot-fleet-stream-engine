"""
Streamlit dashboard for fleet monitoring.
"""

import pandas as pd
import requests
import streamlit as st
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import time

from ws_client import start_websocket

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="IoT Fleet Stream Engine",
    page_icon="🚚",
    layout="wide"
)

start_websocket()
import json
from pathlib import Path

alert_file = Path("last_ws_alert.json")

with st.sidebar:
    
    st.subheader("📡 Live Alert")
    
    if alert_file.exists():

        try:

            realtime_alert = json.loads(
                alert_file.read_text(
                    encoding="utf-8"
                )
            )

            st.error(
                f"{realtime_alert['vehicle_id']}\n\n"
                f"{realtime_alert['alert_type']}"
            )

        except Exception:
            st.info("No alert received")
        
    st.markdown("---")

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
    f"Last refresh: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M:%S')} (Europe/Paris)"
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


@st.cache_data(ttl=60)
def load_vehicles():

    response = requests.get(
        f"{API_URL}/api/vehicles"
    )

    response.raise_for_status()

    return response.json()


telemetry_df = load_telemetry()
alerts_df = load_alerts()
vehicle_list = sorted(load_vehicles())

if telemetry_df.empty:

    st.warning(
        "Waiting for telemetry data..."
    )
    st.stop()

if ("selected_vehicle" not in st.session_state and vehicle_list):
    st.session_state.selected_vehicle = vehicle_list[0]
    
    
if "target_vehicle" not in st.session_state:
    st.session_state.target_vehicle = None

alert_count = len(alerts_df)    

alerts_df["timestamp"] = pd.to_datetime(
    alerts_df["timestamp"]
)

alerts_df["timestamp"] = (
    alerts_df["timestamp"]
    .dt.tz_localize("UTC")
    .dt.tz_convert("Europe/Paris")
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
    width="stretch"
)


if st.session_state.target_vehicle in vehicle_list:

    st.session_state.selected_vehicle = (
        st.session_state.target_vehicle
    )

    st.session_state.target_vehicle = None

elif (
    st.session_state.selected_vehicle
    not in vehicle_list
):
    st.session_state.selected_vehicle = (
        vehicle_list[0]
    )
    
           
selected_vehicle = st.selectbox(
    "Select Vehicle",
    vehicle_list,
    index=vehicle_list.index(
        st.session_state.selected_vehicle
    )
)

st.session_state.selected_vehicle = selected_vehicle


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

if vehicle_df.empty:

    st.info(
        f"No telemetry available yet for "
        f"{selected_vehicle}"
    )

else:

    fig_temp = px.line(
        vehicle_df.sort_values("timestamp"),
        x="timestamp",
        y="temperature",
        title=f"Temperature History - {selected_vehicle}"
    )

    st.plotly_chart(
        fig_temp,
        width="stretch"
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
    
    display_alerts["timestamp"] = (
        display_alerts["timestamp"]
        .dt.strftime("%d/%m/%Y %H:%M:%S")
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
        width="stretch",
        hide_index=True
    )

else:
    st.success(
        "No alerts detected."
    )


st.divider()

st.subheader("⚡ Anomaly Injection")

col1, col2, col3, col4 = st.columns(4)


with col1:

    if st.button(
        "💥 Full Incident",
        width="stretch"
    ):

        response = requests.post(
            f"{API_URL}/api/inject-anomaly/full"
        )

        response.raise_for_status()

        vehicle = response.json()["vehicle_id"]

        st.session_state.target_vehicle = vehicle

        st.toast(
            f"💥 Full incident injected for {vehicle}"
        )

        time.sleep(4)

        st.cache_data.clear()

        st.rerun()
        
        
with col2:

    if st.button(
        "🌡️ High Temperature",
        width="stretch"
    ):

        response = requests.post(
            f"{API_URL}/api/inject-anomaly/temperature"
        )

        vehicle = response.json()["vehicle_id"]

        st.session_state.target_vehicle = vehicle

        st.toast(
            f"🌡️ Temperature anomaly injected for {vehicle}"
        )

        time.sleep(4)

        st.cache_data.clear()

        st.rerun()
        
with col3:

    if st.button(
        "⛽ Low Fuel",
        width="stretch"
    ):

        response = requests.post(
            f"{API_URL}/api/inject-anomaly/fuel"
        )

        vehicle = response.json()["vehicle_id"]

        st.session_state.target_vehicle = vehicle

        st.toast(
            f"⛽ Fuel anomaly injected for {vehicle}"
        )

        time.sleep(4)

        st.cache_data.clear()

        st.rerun()
        
with col4:

    if st.button(
        "🚨 Overspeed",
        width="stretch"
    ):

        response = requests.post(
            f"{API_URL}/api/inject-anomaly/overspeed"
        )

        vehicle = response.json()["vehicle_id"]

        st.session_state.target_vehicle = vehicle

        st.toast(
            f"🚨 Overspeed anomaly injected for {vehicle}"
        )

        time.sleep(4)

        st.cache_data.clear()

        st.rerun()
        

