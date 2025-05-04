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

with open('route_coords.json', 'r') as file:
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

# from math import radians, sin, cos, sqrt, atan2

# def haversine(a, b):
#     # a=(lat,lon) in degrees
#     R = 6371  # km
#     lat1, lon1 = map(radians, a)
#     lat2, lon2 = map(radians, b)
#     dlat = lat2 - lat1
#     dlon = lon2 - lon1
#     u = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
#     return 2*R*atan2(sqrt(u), sqrt(1-u))

# def interpolate(a, b, frac):
#     # Linear interp in lat/lon (OK for small steps)
#     return (a[0] + (b[0]-a[0])*frac,
#             a[1] + (b[1]-a[1])*frac)

# def simulate_constant_speed(route, speed_kmh, dt_sec):
#     step_dist = speed_kmh/3600*dt_sec  # km per dt
#     pts = []   # output (lat,lon) list
#     rem = 0    # leftover distance on current segment
#     seg_i = 0  # index of segment start
#     seg_pos = 0.0  # how far (km) along current seg we've progressed

#     while seg_i < len(route)-1:
#         # current segment endpoints
#         p0, p1 = route[seg_i], route[seg_i+1]
#         seg_len = haversine(p0, p1)
#         # we want to move rem + step_dist along this segment
#         target = rem + step_dist

#         if target <= seg_len:
#             # fraction along this segment
#             frac = target/seg_len
#             new_pt = interpolate(p0, p1, frac)
#             pts.append(new_pt)
#             # advance: this new_pt becomes p0 for next iteration
#             route[seg_i] = new_pt
#             rem = 0
#         else:
#             # move to next segment
#             rem = target - seg_len
#             seg_i += 1
#             # no new point emitted yet; loop continues

#     return pts


# if __name__ == "__main__":
#     # Example route (lat, lon) points
#     # route = [
#     #     (30.033333, 31.233334),
#     #     (30.034000, 31.234000),
#     #     (30.035000, 31.235000),
#     #     (30.036000, 31.236000)
#     # ]

#     speed_kmh = 60  # Speed in km/h
#     dt_sec = 5      # Time step in seconds

#     simulated_route = simulate_constant_speed(route_coords, speed_kmh, dt_sec)
#     for point in simulated_route:
#         print(point)