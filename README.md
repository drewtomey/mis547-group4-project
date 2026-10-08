# Team 4 Group Project - Credit Card Fraud Detection
This repository is for team 4's group project in MIS 547: Fundamentals of Cloud Computing and its Design Strategies. This repo is an end-to-end MLOps pipelne on DigitalOcean (DO). In this project, a fraud detection model is trained on a Droplet, served as a Rest API using App Platform and every prediction is logged in a managged PostgreSQL database.

# dataset
This project uses a ULB Credit Card Fraud Detection dataset from Kaggle. It has 284,807 tranactions with 492 of them being fraud.
URL: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

# Architecture
1. DigitalOcean Spaces  <-->  Droplet (for training)

2. Droplet uploads model to Spaces -> model file is committed to this repo -> App Platform builds and deploys the API from api/

3. Inference API creates prediction results  -->  prediction uploaded to Managed PostgreSQL

Object Storage (DO Spaces)
    - Holds the eaw dataset (```raw_data/```) and trained models (```models/```)

Training (DO Droplet)
    - Droplet downloads the dataset from Spaces, trains the model, and uploads the model artifact to Spaces

Inference API (DO App Platform)
    - Serves ```POST /predict``` using the model commited in this repo under api/

Prediction Log (DO Managed PostgreSQL)
    - Stores predictions. Consists of probability, decision, and timestamp.

Deployment path for a retrained model: train on the Droplet -> artifact lands in Spaces -> download it into api/xgb_fraud_v1.joblib -> commit and push -> App Platform redeploys. This last step is manual. See api/README.md.

# Repo Layout
```training/``` - training script that runs on the Droplet

```api/``` - FastAPI service deployed on App Platform

```api/samples``` - Sample trananctions for testing

```docker/apiDockerfile``` - Container build of the API, used by CI security scan

```.github/workflows/security-scan/yml``` - GitHub Action security scan

# Try it out from the repo root
Base URL: https://mis647-team4-inferenceapi-y4pi5.ondigitalocean.app
Health check:
```curl https://mis647-team4-inferenceapi-y4pi5.ondigitalocean.app/```
(should display ```{"status":"ok"}```)

Fraud tranaction:
```curl -X POST https://mis647-team4-inferenceapi-y4pi5.ondigitalocean.app/predict -H "Content-Type: application/json" -d @api/samples/sample_fraud.json```
(should display ```fraud_probability``` close to 1 and ```"is_fraud": true```)

Ordinary transaction:
```curl -X POST https://mis647-team4-inferenceapi-y4pi5.ondigitalocean.app/predict -H "Content-Type: application/json" \ -d @api/samples/sample_legit.json```
(should display ```fraud_probability``` close to 0 and ```"is_fraud": false```)

# Model results
Latest droplet training run results:
Precision: 0.771
Recall: 0/857
AUPRC: 0.878

# Security Scans
Security scans run on every push to ```main```, every pull request, and on a weekly basis.
1. Static analysis using CodeQL is performed on python code in ```training/``` and ```api```
2. Trivy scans for commited secrets, vulnerable packages, and configs.
3. Trivy scans the API container image in ```docker/api.Dockerfile```
Finding can be found in the Security tab of the repository in GitHub