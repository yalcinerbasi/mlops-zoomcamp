## Problem Description

A Fortune 100 company, Liberty Mutual Insurance has provided a wide range of insurance products and services designed to meet their customers' ever-changing needs for over 100 years.

To ensure that Liberty Mutual’s portfolio of home insurance policies aligns with their business goals, many newly insured properties receive a home inspection. These inspections review the condition of key attributes of the property, including things like the foundation, roof, windows and siding. The results of an inspection help Liberty Mutual determine if the property is one they want to insure.

In this project, your task is to predict a transformed count of hazards or pre-existing damages using a dataset of property information. This will enable Liberty Mutual to more accurately identify high risk homes that require additional examination to confirm their insurability.

### Data Description

Each row in the dataset corresponds to a property that was inspected and given a hazard score ("Hazard"). You can think of the hazard score as a continuous number that represents the condition of the property as determined by the inspection. Some inspection hazards are major and contribute more to the total score, while some are minor and contribute less. The total score for a property is the sum of the individual hazards.

The aim of the competition is to forecast the hazard score based on anonymized variables which are available before an inspection is ordered.




## Instructions

### Set cloud machine and install required programs

```bash
# Configure your AWS acoount
aws configure
# Create key pair to connect AWS
aws ec2 create-key-pair --region eu-central-1 --key-name mlops --query 'KeyMaterial' --output text > ~/.ssh/mlops.pem
chmod 400 ~/.ssh/mlops.pem 
# Launch AWS actions proposed in a Terraform
# Initialize working directory containing Terraform configuration files
cd terraform 
terraform init
# See an execution plan
terraform plan
# Executes the actions proposed in a Terraform 
terraform apply
# Connect remote machine
ssh -i ~/.ssh/mlops.pem ubuntu@$(aws ec2 describe-instances   --query "Reservations[*].Instances[*].PublicIpAddress"   --output=text)
# Download Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.12.0-Linux-x86_64.sh
# Set up Miniconda
bash Miniconda3-py39_4.12.0-Linux-x86_64.sh
# Install docker
sudo apt update
sudo apt install docker.io
# Download Docker-Compose and made it executable
mkdir prog
cd prog
wget https://github.com/docker/compose/releases/download/v2.10.0/docker-compose-linux-x86_64 -O docker-compose
chmod +x docker-compose
# Appending a Path end of bashrc file and reload bashrc:
nano ~/.bashrc
	# export PATH="${HOME}/prog:${PATH}"
source ~/.bashrc

```

### Design Project

```bash

# Create Conda enviroments and activate it
conda create -n mlops-project python==3.9.12
conda activate mlops-project
# Install dependencies
pip install -r requirements.txt
# 3 best features selected which one is categorical
cd feature_importance
python extract_features_importance.py
# Preprocess for Experiment Tracking 
cd ../experiment_tracking
python preprocess_data.py --raw_data_path ../data --dest_path ./output
# Start for Experiment Tracking Service
mlflow server --backend-store-uri sqlite:///backend.db --default-artifact-root ./artifacts
# Activate conda enviroment on new terminal and execute hpo.py to tune the hyperparameters of the model
conda activate mlops-project
python hpo.py --max_evals 10
# Promote the best model to the model registry and you can see mlflow user interface on http://127.0.0.1:5000 
python register_model.py --top_n 1
# Copy Model and DictVectorizer to predition services file
cd ../
python copy_best_model.py
# Execute docker compose yaml file for Prediction Service and MongoDB
docker compose -f docker-compose.yml up -d
# Sending data to the predition service
python send_data.py
# Generate monitoring with Evidently report using Prefect
python prefect_monitoring.py 
# Create a deployment with a CronSchedule
prefect deployment create prefect_deployment.py
# Start Prefect user interface server (http://127.0.0.1:4200)
prefect orion start 

```




