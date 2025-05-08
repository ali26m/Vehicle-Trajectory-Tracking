import json
import time
from pymongo import MongoClient
from datetime import datetime

# Load coordinates from the JSON file
with open('../data/route_coords.json') as f:
    data = json.load(f)
coordinates = data['coordinates']

# MongoDB Atlas URI (replace with your actual URI)
mongo_uri = 'mongodb+srv://abdelrahmanibrahim425:boodyabdo@cluster0.pqexzns.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
client = MongoClient(mongo_uri)

# Database and Collection
db = client["Tracking"]  # Replace with your actual DB name
locations_col = db["Trips"]  # Replace with your collection name

# Car ID to update
car_id = "car_1"

# Loop through coordinates
i = 0
while True:
    if i >= len(coordinates):
        i = 0  # Loop back to the start

    lon, lat = coordinates[i]

    # Update MongoDB with the new location
    locations_col.update_one(
        {"car_id": car_id},
        {
            "$set": {
                "latitude": lat,
                "longitude": lon,
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True  # Create the document if it doesn't exist
    )

    print(f"Updated {car_id} to lat: {lat}, lon: {lon}")

    i += 1
    time.sleep(2)
