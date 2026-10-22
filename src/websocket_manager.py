"""
WebSocket connection manager.
"""

from fastapi import WebSocket


class ConnectionManager:
    """
    Manage active WebSocket connections.
    """

    def __init__(self) -> None:

        self.active_connections: list[WebSocket] = []

    async def connect(
        self,
        websocket: WebSocket
    ) -> None:
        """
        Register a new WebSocket connection.
        """

        await websocket.accept()

        self.active_connections.append(
            websocket
        )

    def disconnect(
        self,
        websocket: WebSocket
    ) -> None:
        """
        Remove a WebSocket connection.
        """

        self.active_connections.remove(
            websocket
        )

    async def broadcast(
        self,
        message: dict,
    ) -> None:
        """
        Send a message to all connected clients.
        """

        print(
            f"CLIENTS={len(self.active_connections)}"
        )

        for connection in self.active_connections:

            print("SENDING MESSAGE")

            await connection.send_json(
                message
            )


manager = ConnectionManager()