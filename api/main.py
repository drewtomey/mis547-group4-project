# Group 4
# MIS 547
# Name: main.py
# v1.0
from fastapi import FastAPI, HTTPException
import joblib
import pandas as pd

app = FastAPI()
model = joblib.load("xgb_fraud_v1.joblib")

FEATURE_ORDER = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]

@app.get("/")

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
        return {"fraud_probability": probability, "is_fraud": probability > 0.5}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))