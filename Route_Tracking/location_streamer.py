import requests
import time
import json
import asyncio
import websockets
import json


host='127.0.0.1'
port=8081

# Define start and end coordinates
start = (30.095747626304206, 31.37558410328589)  # AAST
end = (30.1120, 31.4000)    # Cairo International Airport


# Send the request to Open Source Routing Machine (OSRM) API
response = requests.get(
    f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&geometries=geojson"
)
data = response.json()

# Extract the route coordinates
route_coords = data['routes'][0]['geometry']['coordinates']

# Convert to list of (latitude, longitude) tuples
location = [(lat, lon) for lon, lat in route_coords]

# for coord in location:
#     print(coord)

print("Number of coordinates", len(location))

async def gps_simulation(websocket):

    print(f"Client connected: {websocket.remote_address}")

    try:
        for coord in location:
            
            # Sending coordinates to client
            await websocket.send(json.dumps(coord))
            await asyncio.sleep(2)

            print(f"Sent: ({coord[0]}, {coord[1]})")

    except websockets.exceptions.ConnectionClosed:
        print(f"Client {websocket.remote_address} closed")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    async with websockets.serve(gps_simulation, host, port):
        print(f"Running at ws://{host}:{port}")
        await asyncio.Future()  # Run forever

asyncio.run(main())
