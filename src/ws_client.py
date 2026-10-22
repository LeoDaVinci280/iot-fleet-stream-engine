"""
WebSocket alert listener.
"""

from email.mime import message
import json
import threading

import streamlit as st
from websocket import WebSocketApp
import time

from pathlib import Path

def start_websocket() -> None:
    """
    Start alert listener.
    """

    if "ws_started" in st.session_state:
        return

    st.session_state.ws_started = True

    def on_message(ws, message):

        print("WS MESSAGE RECEIVED")
        print(message)

        Path("last_ws_alert.json").write_text(
            message,
            encoding="utf-8"
        )
        
    def on_open(ws):
        print(
            "WEBSOCKET CLIENT CONNECTED"
        )
        

    def on_close(ws, close_status, msg):
        print(
            "WEBSOCKET CLIENT DISCONNECTED"
        )

    def run():

        while True:

            try:

                print("CONNECTING WEBSOCKET")

                ws = WebSocketApp(
                    "ws://localhost:8000/ws/alerts",
                    on_message=on_message,
                    on_open=on_open,
                    on_close=on_close,
                )

                ws.run_forever()

            except Exception as exc:

                print(
                    f"WebSocket error: {exc}"
                )

            print(
                "WebSocket disconnected. "
                "Retrying in 5 seconds..."
            )

            time.sleep(5)

    threading.Thread(
        target=run,
        daemon=True,
    ).start()
    
