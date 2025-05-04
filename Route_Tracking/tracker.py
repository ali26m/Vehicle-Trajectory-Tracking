import googlemaps
import asyncio
import websockets
import json
import traceback
from datetime import datetime
from math import radians, cos, sin, sqrt, atan2
from dotenv import dotenv_values

Maps_API_KEY = dotenv_values("C:\\Users\\alihi\\ipynb\\Vehicle-Trajectory-Tracking\\Route_Tracking\\.env")

gmaps = googlemaps.Client(key=Maps_API_KEY["Maps_API_KEY"])

eta, distance, ideal_coordinate = 0, 0, []

# Calculate distance between two lat/lon points (in kilometers)
def haversine(lat1, lon1, lat2, lon2):

    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)

    a = sin(d_lat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Radius of Earth in km is 6371
    return 6371 * c

def calculate_speed_distance(lat1, lon1, time1, lat2, lon2, time2):

    distance_km = haversine(lat1, lon1, lat2, lon2)
    # print(f"Distance: {distance_km:.3f} km")

    time_diff_hours = (time2 - time1).total_seconds() / 3600.0

    if time_diff_hours == 0:
        return 0
    
    speed = distance_km / time_diff_hours
    # print(f"speed: {speed:.3f} km/h")

    return speed, distance_km, time_diff_hours

def is_over_speed(lat1, lon1, time1, lat2, lon2, time2, speed_limit=100, distance_limit=0.05):# 0.05 km = 50 meters

    speed, distance, time_diff = calculate_speed_distance(lat1, lon1, time1, lat2, lon2, time2)

    # If the speed is greater than the speed limit and the distance is less than the distance limit, it's unrealistic
    # If the speed is greater than the speed limit and the distance is greater than the distance limit, it's overspeeding
    if speed > speed_limit:
        if distance < distance_limit:
            # print("Unrealistic high speed over short distance")
            is_overspeed = True
        else:
            # print("overspeeding")
            is_overspeed = True
    else:
        is_overspeed = False

    return time_diff, distance, speed, is_overspeed

def is_off_route(lat, lon, ideal_coordinate, tolerance_km=0.2):

    # Check if the current location is within 200 meters of Ideal route
    for route_lat, route_lon in ideal_coordinate:

        if haversine(lat, lon, route_lat, route_lon) <= tolerance_km:
            return False
        
    return True

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

            # Extract the ETA and distance from the leg
            eta = leg['duration']['value'] # In seconds
            distance = leg['distance']['value'] # In meters


            # Decode the polyline to get the route coordinates
            decoded_points = googlemaps.convert.decode_polyline(route['overview_polyline']['points'])

            # Convert the list of dictionaries to a list of tuples (lat, lon)
            ideal_coordinate = [[point['lat'], point['lng']] for point in decoded_points]

            # print(f"ETA: {eta} seconds")
            # print(f"Distance: {distance} meters")
            # print("Number of Points", len(ideal_coordinate))
            
            # Print the ideal points
            # for i, coord in enumerate(ideal_coordinate[0:10]):
            #     print(coord)

            # Save the data to a text file for later use
            with open('ideal_coordinate.txt', 'w') as f:
                for item in ideal_coordinate:
                    f.write(f"{item}\n")
            with open('distance.txt', 'w') as f:
                f.write(f"{distance}\n")
            with open('eta.txt', 'w') as f:
                f.write(f"{eta}\n")

        else:
            print(f"Could not find a route between '{start}' and '{destination}'")

    except googlemaps.exceptions.ApiError as e:
        print(f"Google Maps API Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return eta, distance, ideal_coordinate


async def gps_tracker():
    global eta, distance, ideal_coordinate
    
    prev_lat, prev_lon, prev_time = None, None, None

    try:
        # Connect to WebSocket server
        async with websockets.connect("ws://localhost:8081") as websocket:

            while True: # while True when finished testing. for _ in range(5): for testing only 

                try:
                    # Receive location
                    location = await websocket.recv()
                    location = json.loads(location) # convert string to dict
                    
                    # Get start and destination coordinates from the first message
                    if "start_destination_coordinates" in location:
                        start = location["start_destination_coordinates"]["start"]
                        destination = location["start_destination_coordinates"]["destination"]
                        print(f"Start: {start}")
                        print(f"Destination: {destination}")

                        # uncomment when finished testing
                        eta, distance, ideal_coordinate = get_route_ETA(start, destination)

                        # Uncomment to read from text
                        # Read eta, distance, and ideal_coordinate from text files
                        # with open('eta.txt', 'r') as f:
                        #     eta = int(f.read().strip())
                        # with open('distance.txt', 'r') as f:
                        #     distance = int(f.read().strip())
                        # with open('ideal_coordinate.txt', 'r') as f:
                        #     ideal_coordinate = [list(map(float, line.strip()[1:-1].split(', '))) for line in f.readlines()]

                        # Get the car coordinates and time
                    elif "route_coord" in location:
                        lat, lon = location["route_coord"]
                        time = datetime.strptime(location["time"], "%H:%M:%S").time()
                        time = datetime.combine(datetime.today(), time)
                        

                        # Check if it's the first location. If no, then begin detection
                        if prev_lat is not None and prev_lon is not None and prev_time is not None:
                            
                            time_diff, distance, speed, is_overspeed = is_over_speed(prev_lat, prev_lon, prev_time, lat, lon, time)
                            deviance = is_off_route(lat, lon, ideal_coordinate)
                            
                            print("====================================")
                            print(f"location= {location["route_coord"]}, time= {time}")
                            print(f"Time difference: {time_diff * 60 * 60} seconds")
                            print(f"Distance: {distance * 1000:.3f} m")
                            print(f"Speed: {speed:.3f} km/h")
                            print(f"Deviance: {deviance}")
                            print(f"Is overspeeding: {is_overspeed}")
                            print("====================================")

                        # Update previous location and time
                        prev_lat, prev_lon, prev_time = lat, lon, time

                except websockets.exceptions.ConnectionClosedOK:
                    print("WebSocket connection closed cleanly (1000 OK).")
                    break
                except websockets.exceptions.ConnectionClosedError as e:
                    print(f"Connection closed with error: {e}")
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    traceback.print_exc()

    except Exception as e:
        print(f"Failed to connect or crashed: {e}")
        traceback.print_exc()
    # finally:
        # print(eta, distance)
        # for i, coord in enumerate(ideal_coordinate[0:10]):
        #     print(i, coord)

# For testing 
# get_route_ETA((30.095747626304206, 31.37558410328589), (30.11484871023897, 31.38052118309438))

asyncio.run(gps_tracker())