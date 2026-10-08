# api/

FastAPI inference service. It scores credit card transactions for fraud and logs every prediction to PostgreSQL. It is deployed on DigitalOcean App Platform.

Live URL: `https://mis647-team4-inferenceapi-y4pi5.ondigitalocean.app`

## Files

| File | Purpose |
|---|---|
| `main.py` | The API (two routes) |
| `xgb_fraud_v1.joblib` | The trained XGBoost model, committed to git and loaded at startup |
| `requirements.txt` | Python dependencies |
| `samples/` | Example transactions for testing (`sample_fraud.json`, `sample_legit.json`) |

## Endpoints

### `GET /`
Health check. Returns `{"status": "ok"}`.

### `POST /predict`
Scores one transaction.

**Request:** a JSON object with all 30 model features: `Time`, `V1` through `V28`, and `Amount`. Field order does not matter. The API puts them in the order the model expects. `V1` to `V28` are the dataset's anonymized (PCA-transformed) features. See [`samples/sample_fraud.json`](samples/sample_fraud.json) for a complete example.

**Response (200):**
```json
{"fraud_probability": 0.99999785, "is_fraud": true}
```
`is_fraud` is `true` when `fraud_probability` is above 0.5.

**Errors:** the API returns a message instead of failing silently.

| Case | Status | Response |
|---|---|---|
| One or more features missing | 400 | `{"detail": "Missing fields: [...]"}` listing the missing names |
| Values that cannot be scored (for example, text instead of a number) | 400 | `{"detail": "<error message>"}` |

## Try it

From the repo root:

```bash
# fraud-like transaction -> probability close to 1
curl -X POST https://mis647-team4-inferenceapi-y4pi5.ondigitalocean.app/predict \
  -H "Content-Type: application/json" \
  -d @api/samples/sample_fraud.json

# ordinary transaction -> probability close to 0
curl -X POST https://mis647-team4-inferenceapi-y4pi5.ondigitalocean.app/predict \
  -H "Content-Type: application/json" \
  -d @api/samples/sample_legit.json

# incomplete request -> clear 400 error
curl -X POST https://mis647-team4-inferenceapi-y4pi5.ondigitalocean.app/predict \
  -H "Content-Type: application/json" \
  -d '{"Time": 1}'
```

## Prediction logging

Each successful prediction is inserted into the `predictions` table of the managed PostgreSQL database:

| Column | Type |
|---|---|
| `id` | serial primary key |
| `fraud_probability` | float |
| `is_fraud` | boolean |
| `predicted_at` | timestamp (defaults to now) |

Logging is best-effort. If the database is unreachable, the prediction is still returned and the failure is printed to the app's runtime log.

The database accepts connections only from trusted sources (this app and approved IPs).

## Environment variables

| Variable | Meaning |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string. Set as an **encrypted** environment variable on App Platform and never committed. If unset, the API still serves predictions without logging them. |

## Run locally

```bash
cd api
python3 -m venv api-env
source api-env/bin/activate
pip install -r requirements.txt
export DATABASE_URL="..."
uvicorn main:app --reload
```
Then call `http://127.0.0.1:8000/` with the `curl` commands above, replacing the base URL.

## Deployment

- Deployed on DigitalOcean App Platform from this repo, branch `main`, **source directory `/api`**.
- App Platform detects Python from `requirements.txt` and builds the app. Pushes to `main` redeploy it.
- A separate `docker/api.Dockerfile` (outside this folder) builds the same service as a container image. The security-scan workflow uses it to scan the image. It does not affect the App Platform deployment.

## Updating the model

The deployed model is the file committed at `api/xgb_fraud_v1.joblib`, so every deployment is tied to a git commit. After retraining (see [`../training/README.md`](../training/README.md)):

1. Download `models/xgb_fraud_v1.joblib` from the Space (Control Panel -> Spaces -> the bucket).
2. Replace `api/xgb_fraud_v1.joblib` with it.
3. Commit and push to `main`. App Platform redeploys.
4. Check the deployment is healthy, then run the `curl` commands above. The fraud sample should score close to 1.