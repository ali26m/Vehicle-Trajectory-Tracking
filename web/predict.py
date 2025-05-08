from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import uvicorn

# === Load Encoders and Model ===
try:
    with open('../Anomaly_Detection/Encoders/time_of_day_encoder.pkl', 'rb') as f:
        time_encoder = pickle.load(f)
    with open('../Anomaly_Detection/Encoders/traffic_condition_encoder.pkl', 'rb') as f:
        traffic_encoder = pickle.load(f)
    with open('../Anomaly_Detection/Encoders/road_type_encoder.pkl', 'rb') as f:
        road_encoder = pickle.load(f)
    with open('../Anomaly_Detection/Encoders/weather_conditions_encoder.pkl', 'rb') as f:
        weather_encoder = pickle.load(f)
    with open('../Anomaly_Detection/Models/decision_Tree_classifier.pkl', 'rb') as f:
        tree_model = pickle.load(f)
except Exception as e:
    print(f"Error loading models or encoders: {e}")
    raise e

# === Request Schema ===
class PredictionRequest(BaseModel):
    speed: float
    eta: float
    distance: float
    weather: str
    road: str
    traffic: str
    time_of_day: str
    deviance: int

# === FastAPI App ===
app = FastAPI(title="Anomaly Detection API", version="1.0")

@app.get("/")
def root():
    return {"status": "OK", "message": "Anomaly Detection API is running."}

@app.post("/predict")
def predict(request: PredictionRequest):
    try:
        # Validate categorical values against trained encoder classes
        for label, val, encoder in [
            ("weather", request.weather, weather_encoder),
            ("road", request.road, road_encoder),
            ("traffic", request.traffic, traffic_encoder),
            ("time_of_day", request.time_of_day, time_encoder)
        ]:
            if val not in encoder.classes_:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid {label} value '{val}'. Must be one of {list(encoder.classes_)}"
                )

        # Encode categorical values
        encoded_weather = weather_encoder.transform([request.weather])[0]
        encoded_road = road_encoder.transform([request.road])[0]
        encoded_traffic = traffic_encoder.transform([request.traffic])[0]
        encoded_time = time_encoder.transform([request.time_of_day])[0]

        # Prepare feature vector
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

        prediction = tree_model.predict([features])[0]

        return {
            "prediction": int(prediction),
            "message": "Anomalous" if prediction == 1 else "Normal"
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")

# === Run Server ===
if __name__ == "__main__":
    uvicorn.run("predict:app", host="127.0.0.1", port=8000, reload=True)
