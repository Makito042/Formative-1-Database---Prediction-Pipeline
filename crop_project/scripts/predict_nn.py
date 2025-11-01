import requests
import pandas as pd
import pickle
import numpy as np
from tensorflow.keras.models import load_model
import sys
import os

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Load the saved model, columns, and scaler ---
print("Loading model and preprocessing objects...")
try:
    model = load_model('../models/neural_network_model.h5')
    with open('../models/columns.pkl', 'rb') as f:
        columns = pickle.load(f)
    with open('../models/scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    print("Successfully loaded all files.")
except Exception as e:
    print(f"Error loading files: {e}")
    print("Please ensure 'neural_network_model.h5', 'columns.pkl', and 'scaler.pkl' are in the 'models' directory.")
    exit()
# -------------------------------------------------

# --- Fetch the latest reading from the API ---
print("\nFetching latest reading from the API...")
try:
    response = requests.get("http://127.0.0.1:8000/readings/")
    response.raise_for_status() # Raise an exception for bad status codes
except requests.exceptions.RequestException as e:
    print(f"API request failed: {e}")
    print("Please ensure the FastAPI server is running.")
    exit()

readings = response.json()
if not readings:
    print("No readings found in the database.")
    exit()

latest_reading = readings[-1]
print(f"Latest reading fetched (ID: {latest_reading['id']})")
# ---------------------------------------------

# --- Query the database for categorical feature names ---
# This is necessary because the API returns IDs, but the model was trained on names
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.database.models import Crop, SoilType, GrowthStage

load_dotenv(dotenv_path='../.env')
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    print("DATABASE_URL not found in .env file.")
    exit()

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

crop = db.query(Crop).filter(Crop.id == latest_reading['crop_id']).first()
soil_type = db.query(SoilType).filter(SoilType.id == latest_reading['soil_type_id']).first()
growth_stage = db.query(GrowthStage).filter(GrowthStage.id == latest_reading['growth_stage_id']).first()
db.close()

if not all([crop, soil_type, growth_stage]):
    print("Could not find all related data (crop, soil type, or growth stage) in the database.")
    exit()
# ---------------------------------------------------------

# --- Prepare the data for prediction ---
print("\nPreparing data for prediction...")
data = {
    'crop ID': [crop.name],
    'soil_type': [soil_type.name],
    'Seedling Stage': [growth_stage.name],
    'MOI': [latest_reading['moi']],
    'temp': [latest_reading['temp']],
    'humidity': [latest_reading['humidity']],
}
input_df = pd.DataFrame(data)

# One-hot encode the input data
input_encoded = pd.get_dummies(input_df)

# Align the columns with the training data
input_aligned = input_encoded.reindex(columns=columns, fill_value=0)

# Scale the data using the loaded scaler
input_scaled = scaler.transform(input_aligned)
print("Data prepared successfully.")
# ---------------------------------------

# --- Make a prediction ---
print("\nMaking prediction...")
prediction_prob = model.predict(input_scaled)
prediction = np.argmax(prediction_prob, axis=1)[0]
# -------------------------

print("\n" + "="*30)
print(f"  Prediction for the latest reading: {prediction}")
print("="*30)
