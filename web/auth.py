from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # <-- import this
from pymongo import MongoClient
import hashlib

app = Flask(__name__)
CORS(app)  # <-- allow CORS for all routes

# MongoDB setup
mongo_uri = 'mongodb+srv://abdelrahmanibrahim425:boodyabdo@cluster0.pqexzns.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
client = MongoClient(mongo_uri)
db = client['Authentication_DB']
users_collection = db['user_pass']

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user = users_collection.find_one({"username": username, "password": hashed_password})

    if user:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Invalid username or password."})

if __name__ == '__main__':
    app.run(debug=True)
