from flask import Flask
from flask_socketio import SocketIO
from threading import Thread, Event
import time
from pymongo import MongoClient

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# MongoDB Atlas URI (replace with your actual URI)
mongo_uri = 'mongodb+srv://abdelrahmanibrahim425:boodyabdo@cluster0.pqexzns.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
client = MongoClient(mongo_uri)

# Database and Collection
db = client['Tracking']  # Replace with your actual database name
cars_collection = db['Trips']  # Replace with your collection name

def emit_locations():
    while True:
        locations = []
        for car in cars_collection.find():
            locations.append({
                "car_id": car["car_id"],
                "latitude": car["latitude"],
                "longitude": car["longitude"]
            })
        socketio.emit("location_update", locations)
        time.sleep(1)  # Broadcast every 1 second

@app.route('/')
def index():
    return "SocketIO Server Running"

# Start the background thread
@socketio.on('connect')
def handle_connect():
    print('Client connected')

if __name__ == '__main__':
    Thread(target=emit_locations, daemon=True).start()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
