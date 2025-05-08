from pymongo import MongoClient

# MongoDB URI (replace with your actual URI)
mongo_uri = 'mongodb+srv://abdelrahmanibrahim425:boodyabdo@cluster0.pqexzns.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

# Connect to MongoDB
client = MongoClient(mongo_uri)

# List databases to check connection
try:
    print("Databases: ", client.list_database_names())
except Exception as e:
    print("Error connecting to MongoDB Atlas:", e)

# Select your database and collection
db = client['Tracking']  # Replace with your actual database name
cars_collection = db['Trips']  # Collection name

# Sample document to insert
car_data = {
    "car_id": "unique_car_id_123",
    "latitude": 30.095848,
    "longitude": 31.3756539,
    "timestamp": "2025-05-08T15:30:00",
    "status": "active"
}

# Insert the document into the collection
try:
    result = cars_collection.insert_one(car_data)
    if result.acknowledged:
        print("Document inserted successfully!")
    else:
        print("Insertion failed.")
except Exception as e:
    print("Error during insertion:", e)
