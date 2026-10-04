# Group 4
# MIS 547
# Name: main.py
# v1.0
from fastapi import FastAPI, HTTPException
import joblib
import pandas as pd
import psycopg2
import os
import io
import boto3

app = FastAPI()
model = joblib.load("xgb_fraud_v1.joblib")

FEATURE_ORDER = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]
DATABASE_URL = os.environ.get("DATABASE_URL")

@app.get("/")

# loads model 
def load_model_from_space():
    region = os.getenv("DO_SPACES_REGION", "sfo3")
    bucket = os.getenv("DO_SPACES_BUCKET", "mis547-group4-space")
    key = "models/xgb_fraud_v1.joblib"
    endpoint = os.environ.get("SPACES_ENDPOINT", f"https://{region}.digitaloceanspaces.com").strip()

    s3_client= boto3.client(
        "s3",
        region_name=region,
        endpoint_url=endpoint,
        aws_access_key_id= os.environ["DO_SPACES_ACCESS_KEY"],
        aws_secret_access_key=os.environ["DO_SPACES_SECRET_KEY"],
    )

def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(transaction: dict):
    missing = set(FEATURE_ORDER) - transaction.keys()
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing fields: {sorted(missing)}")
    try:
        df = pd.DataFrame([transaction])[FEATURE_ORDER]
        probability = float(model.predict_proba(df)[0][1])
        is_fraud = probability > 0.5

        if DATABASE_URL:
            try:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO predictions (fraud_probability, is_fraud) VALUES (%s, %s)",
                    (probability, is_fraud),
                )
                conn.commit()
                cur.close()
                conn.close()
            except Exception as log_err:
                print(f"Logging failed: {log_err}")

        return {"fraud_probability": probability, "is_fraud": is_fraud}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))