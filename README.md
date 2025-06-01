# Vehicle Trajectory Tracking

A decision support system for real-time vehicle tracking, anomalous events detection, and trajectory data analysis. It shows car locations on a map, classifies behavior using a machine learning model, and includes dashboards and chatbot features.

---

## Features

- Track real-time car positions from simulated or live data
- Calculate speed and detect route deviation
- Get weather conditions using an external API
- Classify situations using a Decision Tree model
- Trigger alerts based on classification
- Web-based dashboard for visualizing car locations and behavior
- Natural language chatbot to query data
- User authentication connected to MongoDB

---

## How It Works
![DSS Arch (1)](https://github.com/user-attachments/assets/f77eac59-7682-4f40-8de6-01bf027963a9)

1. `add_cars.py` reads simulated car routes and adds them to MongoDB.
2. `send_location.py` sends periodic location updates from the cars.
3. `tracker.py` calculates speed, detects route deviations, and send payload for classification.
4. `FastAPI` serves the machine learning classification model.
5. `get-car.py` fetches data from MongoDB and updates the frontend.
6. The web app shows real-time data using a map. Dashboard for data analysis.
7. A chatbot allows querying data in natural language.

---

## Screenshots from the project

- Map Page:
![image](https://github.com/user-attachments/assets/4f2bf058-edf3-4bdd-9675-ea68f6ed237e)
- Dashboard Page:
![image](https://github.com/user-attachments/assets/ea1e39ff-2cc6-4297-b9f5-b2a51921cb53)
  
