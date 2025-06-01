import asyncio
from pymongo import MongoClient
import socketio
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

# Create a Socket.IO ASGI server
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = FastAPI()
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

# MongoDB Connection
mongo_uri = "mongodb+srv://alihisham26m:ali-tracking@cluster0.pqexzns.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri)
db = client["Tracking"]
cars_collection = db["Trips"]

# ✅ Background coroutine to emit car locations every second
async def emit_locations():
    while True:
        locations = []
        for car in cars_collection.find():
            locations.append({
                "car_id": car["car_id"],
                "latitude": car["latitude"],
                "longitude": car["longitude"]
            })
        await sio.emit("location_update", locations)
        await asyncio.sleep(1)

# Start async background task properly
@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(emit_locations())

# HTTP root endpoint
@app.get("/")
async def root():
    return JSONResponse(content={"message": "200 OK"}, status_code=200)

# Socket.IO events
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

uvicorn.run("get_car:socket_app", host="0.0.0.0", port=5000, reload=True)