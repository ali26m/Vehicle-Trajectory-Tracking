from flask_cors import CORS
from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

mongo_uri = 'mongodb+srv://abdelrahmanibrahim425:boodyabdo@cluster0.pqexzns.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
client = MongoClient(mongo_uri)

db = client['Tracking']
cars_collection = db['Trips']

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

@app.route('/track-location', methods=['POST'])
def track_location():
    print("hooy")
    try:
        data = request.get_json()

        print("Request received!")
        print(f"Car ID: {data.get('car_id')}")
        print(f"Latitude: {data.get('latitude')}")
        print(f"Longitude: {data.get('longitude')}")

        car_id = data['car_id']
        latitude = data['latitude']
        longitude = data['longitude']

        # Save to MongoDB
        result = cars_collection.update_one(
            {"car_id": car_id},
            {
                "$set": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )

        return jsonify({"message": "Location tracked successfully"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
