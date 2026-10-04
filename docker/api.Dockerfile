# Group 4
# MIS 547
# Name: api.Dockerfile
# v1.0
# Container image for the inference API.
# This file lives in docker/ so DigitalOcean App Platform keeps using its
# own Python build for the deployed app. The security-scan workflow builds and scans it.

FROM python:3.12-slim

# XGBoost needs the OpenMP runtime on Linux
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrades pip in the base image as it is vulnerable.
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py xgb_fraud_v1.joblib ./

# run as a non-root user
RUN useradd --create-home app
USER app

EXPOSE 8080

# healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
