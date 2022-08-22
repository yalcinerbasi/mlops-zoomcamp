import logging
import os
import pickle
import uuid

from flask import Flask, jsonify, request
from pymongo import MongoClient


MONGO_ADDRESS = os.getenv("MONGO_ADDRESS", "mongodb://localhost:27017/")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "hazard_prediction")
LOGGED_MODEL = os.getenv("MODEL_FILE", "model.pkl")
LOGGED_DV = os.getenv("DV_FILE", "dv.pkl")
MODEL_VERSION = os.getenv("MODEL_VERSION", "1")

with open(LOGGED_MODEL, 'rb') as f_in:
    model = pickle.load(f_in)

with open(LOGGED_DV, 'rb') as f_in:
    dv = pickle.load(f_in)


mongo_client = MongoClient(MONGO_ADDRESS)
mongo_db = mongo_client[MONGO_DATABASE]
mongo_collection = mongo_db.get_collection("data")


app = Flask("Hazard-Prediction-Service")
logging.basicConfig(level=logging.INFO)


def prepare_features(hazard):
    """Function to prepare features before making prediction"""

    record = hazard.copy()

    features = dv.transform([record])
   
    return features, record


def save_db(record, pred_result):
    """Save data to mongo db collection"""

    rec = record.copy()
    rec["prediction"] = pred_result[0]
    mongo_collection.insert_one(rec)



@app.route("/", methods=["GET"])
def get_info():
    """Function to provide info about the app"""
    info = """<H1>Ride Prediction Service</H1>
              <div class="Data Request"> 
                <H3>Data Request Example</H3> 
                <div class="data">
                <p> "hazard = {
                    "T1_V16": B,
                    "T1_V1": 15,
                    "T2_V2": 11
                    }"
                </p>
                </div>    
               </div>"""
    return info

@app.route("/predict-duration", methods=["POST"])
def predict_duration():
    """Function to predict duration"""

    hazard = request.get_json()
    features, record = prepare_features(hazard)

    prediction = model.predict(features)
    hazard_id = str(uuid.uuid4())
    pred_data = {
            "hazard_id": hazard_id,
            "T1_V16": record["T1_V16"],
            "T1_V1": record["T1_V1"],
            "T2_V2": record["T1_V2"],
            "status": 200,
            "Hazard": prediction[0],
            "model_version": MODEL_VERSION
            }

    save_db(record, prediction)

    result = {
        "statusCode": 200,
        "data" : pred_data
        }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)
