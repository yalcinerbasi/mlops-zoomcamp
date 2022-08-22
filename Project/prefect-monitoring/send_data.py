import json
import uuid
from datetime import datetime
import pandas as pd
import requests

table = pd.read_csv("../data/train.csv")\
          .sample(n=100, random_state=42) #100 rows sampled
data = table.copy()


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


with open("target.csv", 'w') as f_target:
    for index, row in data.iterrows():
        row['id'] = str(uuid.uuid4())
        hazard = row['Hazard']
        f_target.write(f"{row['id']},{hazard}\n")
        resp = requests.post("http://127.0.0.1:9696/predict-duration",
                             headers={"Content-Type": "application/json"},
                             data=row.to_json()).json()
        print(f"prediction: {resp['data']['Hazard']}")
