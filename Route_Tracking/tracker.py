import googlemaps
import requests
import asyncio
import websockets
import json
import traceback
from datetime import datetime
from math import radians, cos, sin, sqrt, atan2
from dotenv import dotenv_values
import pickle
# import shap
import numpy as np
import httpx

# # Load encoders
# with open('Anomaly_Detection/Encoders/time_of_day_encoder.pkl', 'rb') as f:
#     time_encoder = pickle.load(f)
# with open('Anomaly_Detection/Encoders/traffic_condition_encoder.pkl', 'rb') as f:
#     traffic_encoder = pickle.load(f)
# with open('Anomaly_Detection/Encoders/road_type_encoder.pkl', 'rb') as f:
#     road_encoder = pickle.load(f)
# with open('Anomaly_Detection/Encoders/weather_conditions_encoder.pkl', 'rb') as f:
#     weather_encoder = pickle.load(f)

# # Load trained Decision Tree model
# with open('Anomaly_Detection/Models/decision_Tree_classifier.pkl', 'rb') as f:
#     tree_model = pickle.load(f)
    
    # Initialize SHAP TreeExplainer once
    # explainer = shap.TreeExplainer(tree_model)

secrets = dotenv_values("C:\\Users\\alihi\\ipynb\\Vehicle-Trajectory-Tracking\\Route_Tracking\\.env")

gmaps = googlemaps.Client(key=secrets["Maps_API_KEY"])

eta, distance, ideal_coordinate = 0, 0, []

def get_time_of_day(hour):
    if 5 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 17:
        return 'Afternoon'
    elif 17 <= hour < 21:
        return 'Evening'
    else:
        return 'Night'

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

def is_over_speed(lat1, lon1, time1, lat2, lon2, time2, speed_limit=130, distance_limit=0.05):# 0.05 km = 50 meters

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
        directions_result = gmaps.directions(
            origin=start,
            destination=destination,
            mode="driving",
            departure_time="now",  # Needed for traffic info
            traffic_model="best_guess"
        )

        if directions_result:

            # Get the first route (ideal)
            route = directions_result[0]

            # Get the first 'leg' of the route
            leg = directions_result[0]['legs'][0]

            # Extract the ETA and distance from the leg
            eta = leg['duration']['value'] # In seconds
            distance = leg['distance']['value'] # In meters

            # Get the traffic condition based on the ETA with and without traffic
            eta_with_traffic = leg.get('duration_in_traffic', {}).get('value')
            if eta_with_traffic and eta:
                traffic_ratio = eta_with_traffic / eta

                if traffic_ratio <= 1.2:
                    traffic_condition = "Light"
                elif traffic_ratio <= 1.5:
                    traffic_condition = "Moderate"
                else:
                    traffic_condition = "Heavy"

            #get the road type based on the instructions
            for step in leg['steps']:
                instruction = step['html_instructions'].lower()
                
                if 'highway' in instruction or 'freeway' in instruction or 'expressway' in instruction:
                    road_type = 'Highway'
                elif 'st' in instruction or 'rd' in instruction or 'ave' in instruction:
                    road_type = 'Urban'
                else:
                    road_type = 'Rural'

                # get weather condition based on the instructions
                url = f"https://api.weatherapi.com/v1/current.json?key={secrets["weather_API_KEY"]}&q={start[0]},{start[1]}"
                response = requests.get(url)
                data = response.json()
                condition_text = data['current']['condition']['text']
                condition_text = condition_text.lower()

                # map weather conditions to categories
                if 'fog' in condition_text or 'mist' in condition_text or 'haze' in condition_text:
                    weather_condition = 'Foggy'
                elif 'rain' in condition_text or 'drizzle' in condition_text or 'shower' in condition_text:
                    weather_condition = 'Rainy'
                elif 'cloud' in condition_text or 'overcast' in condition_text:
                    weather_condition = 'Cloudy'
                elif 'sun' in condition_text or 'clear' in condition_text:
                    weather_condition = 'Sunny'


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
            # with open('ideal_coordinate.txt', 'w') as f:
            #     for item in ideal_coordinate:
            #         f.write(f"{item}\n")
            # with open('distance.txt', 'w') as f:
            #     f.write(f"{distance}\n")
            # with open('eta.txt', 'w') as f:
            #     f.write(f"{eta}\n")

        else:
            print(f"Could not find a route between '{start}' and '{destination}'")

    except googlemaps.exceptions.ApiError as e:
        print(f"Google Maps API Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return eta, distance, traffic_condition, road_type, weather_condition, ideal_coordinate


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
                        eta, distance, traffic_condition, road_type, weather_condition, ideal_coordinate = get_route_ETA(start, destination)

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
                            time_of_day_str = get_time_of_day(time.hour)
                            
                            print("====================================")
                            print(f"location= {location["route_coord"]}, time= {time}")
                            print(f"Time difference: {time_diff * 60 * 60} seconds")
                            print(f"Distance: {distance * 1000:.3f} m")
                            print(f"Speed: {speed:.3f} km/h")
                            print(f"Deviance: {deviance}") # route anomaly
                            print(f"Time of the day: {get_time_of_day(time.hour)}")
                            print(f"Is overspeeding: {is_overspeed}")
                            print(f"Traffic condition: {traffic_condition}")
                            print(f"Road type: {road_type}")
                            print(f"Weather condition: {weather_condition}")
                            print("====================================")

                            # Prepare the data for prediction
                            # encoded_time = time_encoder.transform([get_time_of_day(time.hour)])[0]
                            # encoded_traffic = traffic_encoder.transform([traffic_condition])[0]
                            # encoded_road = road_encoder.transform([road_type])[0]
                            # encoded_weather = weather_encoder.transform([weather_condition])[0]

                            # # Prepare input features for model
                            # features = np.array([[
                            #     speed,
                            #     eta,
                            #     distance,
                            #     encoded_weather,
                            #     encoded_road,
                            #     encoded_traffic,
                            #     encoded_time,
                            #     int(deviance),
                            # ]])

                            # Make prediction
                            # prediction = tree_model.predict(features)[0]

                            # if prediction == 1:
                            #     print("======Suspicious activity detected======")

                            payload = {
                                "speed": speed,
                                "eta": eta,
                                "distance": distance,
                                "weather": weather_condition,
                                "road": road_type,
                                "traffic": traffic_condition,
                                "time_of_day": time_of_day_str,
                                "deviance": int(deviance)
                            }

                            async with httpx.AsyncClient() as client:
                                response = await client.post("http://127.0.0.1:8000/predict", json=payload)

                            if response.status_code == 200:
                                result = response.json()
                                print(f"Prediction: {result['message']} (Label={result['prediction']})")
                            else:
                                print(f"Prediction API error: {response.status_code} - {response.text}")




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

# For testing 
# get_route_ETA((30.095747626304206, 31.37558410328589), (30.11484871023897, 31.38052118309438))

asyncio.run(gps_tracker())