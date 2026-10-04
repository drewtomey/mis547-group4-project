# Group 4
# MIS 547
# Name: docker/api.Dockerfile
# v1.0
# Container image for the inference API. Build context is the api/ folder:
#   docker build -f docker/api.Dockerfile -t fraud-api api/
# This file lives in docker/ (not api/) so DigitalOcean App Platform keeps using its
# own Python build for the deployed app. The security-scan workflow builds and scans it.

FROM python:3.12-slim

# XGBoost needs the OpenMP runtime on Linux
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py xgb_fraud_v1.joblib ./

# run as a non-root user
RUN useradd --create-home app
USER app

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
