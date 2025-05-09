from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # <-- CORS import
from pydantic import BaseModel
import pickle
import uvicorn

# ========== Load Encoders and Model ==========

try:
    # with open('C:\\Users\\alihi\\ipynb\\Vehicle-Trajectory-Tracking\\Machine_Learning_Model\\Encoders\\time_of_day_encoder.pkl', 'rb') as f:
    with open('..\\Machine_Learning_Model\\Encoders\\time_of_day_encoder.pkl', 'rb') as f:
        time_encoder = pickle.load(f)
    with open('..\\Machine_Learning_Model\\Encoders\\traffic_condition_encoder.pkl', 'rb') as f:
        traffic_encoder = pickle.load(f)
    with open('..\\Machine_Learning_Model\\Encoders\\road_type_encoder.pkl', 'rb') as f:
        road_encoder = pickle.load(f)
    with open('..\\Machine_Learning_Model\\Encoders\\weather_conditions_encoder.pkl', 'rb') as f:
        weather_encoder = pickle.load(f)
    with open('..\\Machine_Learning_Model\\Models\\decision_Tree_classifier.pkl', 'rb') as f:
        tree_model = pickle.load(f)
except Exception as e:
    print(f"Error loading models or encoders: {e}")
    raise e

# ========== Create FastAPI App ==========

app = FastAPI(title="Anomaly Detection API", version="1.0")

# ========== CORS Middleware Setup ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # Allow frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (POST, GET, etc.)
    allow_headers=["*"],
)

# ========== Define Request Schema ==========

class PredictionRequest(BaseModel):
    speed: float
    eta: float
    distance: float
    weather: str
    road: str
    traffic: str
    time_of_day: str
    deviance: int

# ========== Routes ==========

@app.get("/")
def root():
    return {"status": "OK", "message": "Anomaly Detection API is running."}

@app.post("/predict")
def predict(request: PredictionRequest):
    try:
        # Encode input categorical features
        encoded_weather = weather_encoder.transform([request.weather])[0]
        encoded_road = road_encoder.transform([request.road])[0]
        encoded_traffic = traffic_encoder.transform([request.traffic])[0]
        encoded_time = time_encoder.transform([request.time_of_day])[0]

        # Create feature vector
        features = [
            request.speed,
            request.eta,
            request.distance,
            encoded_weather,
            encoded_road,
            encoded_traffic,
            encoded_time,
            request.deviance
        ]

        # Make prediction
        prediction = tree_model.predict([features])[0]

        return {
            "prediction": int(prediction),
            "message": "Anomalous" if prediction == 1 else "Normal"
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")

# ========== Run with Uvicorn ==========

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
