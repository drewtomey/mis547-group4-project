# Group 4
# MIS 547
# Name: train_fraud_model.py
# v1.1
# This script is used to train the model that will be added to the api/ directory in the repository.
# Original Dataset: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

# imports modules needed
import time
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, average_precision_score
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier
import joblib
import boto3

# sets vars for data, model directory, and seed value used in future steps
DATA_PATH = "data/creditcard.csv"
MODEL_DIR = "models"
RANDOM_STATE = 42

# connects to DigitalOcean Spaces using credentials from environment variables
def spaces_client():
    region = os.environ.get("DO_SPACES_REGION", "sfo3")
    endpoint = os.environ.get("SPACES_ENDPOINT", f"https://{region}.digitaloceanspaces.com").strip()
    return boto3.client(
        "s3",
        region_name=region,
        endpoint_url =endpoint,
        aws_access_key_id=os.environ["DO_SPACES_ACCESS_KEY"],
        aws_secret_access_key=os.environ["DO_SPACES_SECRET_KEY"],
    )
 
# pulls the raw dataset from Spaces into data/
def download_data():
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    spaces_client().download_file(os.environ["SPACES_BUCKET"], "raw_data/creditcard.csv", DATA_PATH)
    print("Downloaded dataset from Spaces")

# reads the .csv into memory and prints class imbalance
def load_data(path):
    df = pd.read_csv(path)
    print(f"Loaded shape: {df.shape}")
    print("Class balance:")
    print(df["Class"].value_counts())
    return df
 
# splits data into training and testing sets (80/20)
def split_data(df):
    X = df.drop(columns=["Class"])
    y = df["Class"]
    return train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )
 
# uses SMOTE to generate fraud examples to better train the model 
def resample_training_data(X_train, y_train):
    smote = SMOTE(random_state=RANDOM_STATE)
    X_res, y_res = smote.fit_resample(X_train, y_train)
    print("Post-SMOTE class balance:")
    print(y_res.value_counts())
    return X_res, y_res
 
 # logistic regression (for comparison)
def train_logreg(X_train, y_train):
    start = time.time()
    model = LogisticRegression(max_iter=1000).fit(X_train, y_train)
    elapsed = time.time() - start
    print(f"LogReg trained in {elapsed:.1f}s")
    return model, elapsed
 
 # xgboost
def train_xgboost(X_train, y_train):
    start = time.time()
    model = XGBClassifier(eval_metric="aucpr", random_state=RANDOM_STATE)
    model.fit(X_train, y_train)
    elapsed = time.time() - start
    print(f"XGBoost trained in {elapsed:.1f}s")
    return model, elapsed
 
 # scores model agaist test set
def evaluate(name, model, X_test, y_test):
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]
    print(f"\n--- {name} ---")
    print(classification_report(y_test, preds, digits=3))
    print("AUPRC:", average_precision_score(y_test, probs))
 
 # runs full pipeline and saves to disk for api
def main():
    download_data()
    df = load_data(DATA_PATH)
    X_train, X_test, y_train, y_test = split_data(df)
    X_train_res, y_train_res = resample_training_data(X_train, y_train)
 
    logreg, logreg_time = train_logreg(X_train_res, y_train_res)
    xgb, xgb_time = train_xgboost(X_train_res, y_train_res)
 
    evaluate("LogReg", logreg, X_test, y_test)
    evaluate("XGBoost", xgb, X_test, y_test)
 
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, "xgb_fraud_v1.joblib")
    joblib.dump(xgb, model_path)
    print(f"\nSaved model artifact to {model_path}")
 
    spaces_client().upload_file(
        model_path,
        os.environ["DO_SPACES_BUCKET"],
        "models/xgb_fraud_v1.joblib",
    )
    print("Uploaded model artifact to Team 4 Spaces")
 
    print("\n--- Timing summary ---")
    print(f"LogReg training time: {logreg_time:.1f}s")
    print(f"XGBoost training time: {xgb_time:.1f}s")
main()
