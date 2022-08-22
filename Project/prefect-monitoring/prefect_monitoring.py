import json
import os
import pickle
from datetime import datetime

import pandas as pd 
import pyarrow.parquet as pq
from evidently import ColumnMapping
from evidently.dashboard import Dashboard
from evidently.dashboard.tabs import DataDriftTab, RegressionPerformanceTab
from evidently.model_profile import Profile
from evidently.model_profile.sections import (
    DataDriftProfileSection, RegressionPerformanceProfileSection)
from prefect import flow, task
from pymongo import MongoClient

MONGO_CLIENT_ADDRESS = "mongodb://localhost:27017/"
MONGO_DATABASE = "prediction_service"
PREDICTION_COLLECTION = "data"
REPORT_COLLECTION = "report"
REFERENCE_DATA_FILE = "../data/train.csv" 
TARGET_DATA_FILE = "target.csv"
MODEL_FILE = os.getenv('MODEL_FILE', '../prediction_service/model.pkl')
DV_FILE = os.getenv('DV_FILE', '../prediction_service/dv.pkl')

@task
def upload_target(filename):
    client = MongoClient(MONGO_CLIENT_ADDRESS)
    collection = client.get_database(MONGO_DATABASE).get_collection(PREDICTION_COLLECTION)
    with open(filename) as f_target:
        for line in f_target.readlines():
            row = line.split(",")
            collection.update_one({"id": row[0]},
                                  {"$set": {"target": float(row[1])}}
                                 )



@task
def load_reference_data(filename):
    
    with open(MODEL_FILE, 'rb') as f_in:
        model = pickle.load(f_in)
    with open(DV_FILE, 'rb') as f_in:
        dv = pickle.load(f_in)

    reference_data = pd.read_csv(filename).sample(n=5000,random_state=42) #Monitoring for 1st 5000 records
    

    # add target column
    reference_data = reference_data.rename(columns={"Hazard":"target"})
 
    features = ['T1_V16', 'T1_V1', 'T2_V2']
    x_pred = dv.transform(reference_data[features].to_dict(orient='records'))

    reference_data['prediction'] = model.predict(x_pred)
    return reference_data


@task
def fetch_data():
    client = MongoClient(MONGO_CLIENT_ADDRESS)
    data = client.get_database(MONGO_DATABASE).get_collection(PREDICTION_COLLECTION).find()
    df = pd.DataFrame(list(data))
    return df

@task
def run_evidently(ref_data, data):


    profile = Profile(sections=[DataDriftProfileSection(), RegressionPerformanceProfileSection()])
    mapping = ColumnMapping(prediction="prediction", numerical_features=['T1_V1','T2_V2'],
                            categorical_features=['T1_V16'])
    profile.calculate(ref_data, data, mapping)

    dashboard = Dashboard(tabs=[DataDriftTab(), RegressionPerformanceTab(verbose_level=0)])
    dashboard.calculate(ref_data, data, mapping)
    return json.loads(profile.json()), dashboard


@task
def save_report(result):
    """Save evidendtly profile for hazard prediction to mongo server"""

    client = MongoClient(MONGO_CLIENT_ADDRESS)
    collection = client.get_database(MONGO_DATABASE).get_collection(REPORT_COLLECTION)
    collection.insert_one(result)

@task
def save_html_report(result, filename_suffix=None):
    """Create evidently html report file for hazard prediction"""
    
    if filename_suffix is None:
        filename_suffix = datetime.now().strftime('%Y-%m-%d-%H-%M')
    
    result.save(f"hazard_prediction_drift_report_{filename_suffix}.html")


@flow
def batch_analyze():
    upload_target(TARGET_DATA_FILE)
    ref_data = load_reference_data(REFERENCE_DATA_FILE).result()
    data = fetch_data().result()
    profile, dashboard = run_evidently(ref_data, data).result()
    save_report(profile)
    save_html_report(dashboard)

batch_analyze()
