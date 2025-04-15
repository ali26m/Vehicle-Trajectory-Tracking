import asyncio
import websockets
import json

async def gps_tracker():

    # Connect to WebSocket server
    async with websockets.connect("ws://localhost:8081") as websocket:
        while True:
            # Receive location
            message = await websocket.recv()
            location = json.loads(message)
            
            print(f"Received: ({location[0]}, {location[1]})")

asyncio.run(gps_tracker())
