import os
import shutil 
dir = os.getcwd()

# Copy Model file which changing artifacts
beginning = './experiment_tracking/artifacts/'
mid = os.listdir(beginning)[0]
mid2 = os.listdir(beginning+mid)[0]
end = 'artifacts/model/'
fullpath = os.path.join(beginning, mid, mid2, end,'model.pkl')
shutil.copy2(fullpath,'./prediction_service/')

# Copy DictVectorizer File
shutil.copy2('./experiment_tracking/output/dv.pkl','./prediction_service/')