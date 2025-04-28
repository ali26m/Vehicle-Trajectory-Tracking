import googlemaps
import asyncio
import websockets
import json
from dotenv import dotenv_values

Maps_API_KEY = dotenv_values("C:\\Users\\alihi\\ipynb\\Vehicle-Trajectory-Tracking\\Route_Tracking\\.env")

gmaps = googlemaps.Client(key=Maps_API_KEY["Maps_API_KEY"])


def get_route_ETA(start, destination):

    try:

        # Get directions from Google Maps API
        # Use 'driving' for driving directions. 'now' for traffic-based ETA
        directions_result = gmaps.directions(start, destination, mode="driving", departure_time="now")

        if directions_result:

            # Get the first route (ideal)
            route = directions_result[0]

            # Get the first 'leg' of the route
            leg = directions_result[0]['legs'][0]

            duration = leg['duration']['value'] # In seconds
            distance = leg['distance']['value'] # In meters

            print(f"ETA: {duration} seconds")
            print(f"Distance: {distance} meters")

            # Decode the polyline to get the route coordinates
            decoded_points = googlemaps.convert.decode_polyline(route['overview_polyline']['points'])

            # Convert the list of dictionaries to a list of tuples (lat, lon)
            ideal_coordinate = [(point['lat'], point['lng']) for point in decoded_points]

            print("Number of Points", len(ideal_coordinate))
            # Print the ideal points
            # for i, coord in enumerate(ideal_coordinate[0:10]):
            #     print(i, coord)

        else:
            print(f"Could not find a route between '{start}' and '{destination}'")

    except googlemaps.exceptions.ApiError as e:
        print(f"Google Maps API Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return duration, distance, ideal_coordinate


async def gps_tracker():

    # Connect to WebSocket server
    async with websockets.connect("ws://localhost:8081") as websocket:
        while True:
            # Receive location
            message = await websocket.recv()
            location = json.loads(message)
            
            if "coord" in location:
                start = location["coord"]["start"]
                destination = location["coord"]["destination"]
                print(f"Start: {start}")
                print(f"Destination: {destination}")

                duration, distance, ideal_coordinate = get_route_ETA(start, destination)

            else: 
                print(f"Received: ({location[0]}, {location[1]})")

# For testing 
get_route_ETA((30.095747626304206, 31.37558410328589), (30.1120, 31.4000))

# asyncio.run(gps_tracker())


