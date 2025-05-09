import requests
import time
import json
import asyncio
import websockets
import json
from datetime import datetime
import traceback

host='127.0.0.1'
port=8081
# Define start and end coordinates
start = [30.095747626304206, 31.37558410328589]  # GIS AAST
destination = [30.0976405, 31.3717443]    # AAST Clinic

with open('../Data/Location and maps data/route_coords.json', 'r') as file:
    route_coords = json.load(file)

# Step 2: Extract the coordinates list
coordinates = route_coords['coordinates']
route_coords = [[lat, lon] for lon, lat in route_coords["coordinates"]]

# print(route_coords[0:10])
print("Number of coordinates", len(route_coords))

async def gps_simulation(websocket):

    print(f"Client connected: {websocket.remote_address}")

    start_destination_coordinates = {
        "start_destination_coordinates":{
            "start": start,
            "destination": destination,
        }
    }

    # Send start and destination coordinates to client
    await websocket.send(json.dumps(start_destination_coordinates))
    print(f"Sent: {start_destination_coordinates}")

    try:
        for coord in route_coords:
            
            coord = {
                    "route_coord": coord,
                    "time": datetime.now().time().strftime("%H:%M:%S")
                }

            # Sending coordinates to client
            await websocket.send(json.dumps(coord))
            await asyncio.sleep(2)

            print(f"Sent: {coord}")

    except websockets.exceptions.ConnectionClosed:
        print(f"Client {websocket.remote_address} closed")
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()


async def main():
    async with websockets.serve(gps_simulation, host, port):
        print(f"Running at ws://{host}:{port}")
        await asyncio.Future()  # Run forever

asyncio.run(main())
