# training/

Trains the fraud-detection model and runs on a DigitalOcean Droplet.

## What `train_fraud_model.py` does

1. Downloads `raw_data/creditcard.csv` from the Space into `data/`
2. Loads the data and prints the class balance.
3. Splits it into train and test sets (80/20).
4. Balances the **training set only** with SMOTE (synthetic fraud examples). The test set is never resampled.
5. Trains a Logistic Regression baseline and an XGBoost model. Prints training times.
6. Evaluates both on the test set and outputs precision, recall, and AUPRC.
7. Saves the XGBoost model to `models/xgb_fraud_v1.joblib` and uploads it to the Space at `models/xgb_fraud_v1.joblib`

The random seed is fixed (`RANDOM_STATE = 42`), so reruns use the same split.

## Files

| File | Purpose |
|---|---|
| `train_fraud_model.py` | The whole pipeline (download, preprocess, train, evaluate, save, upload) |
| `requirements.txt` | Python dependencies |
| `data/` | Local copy of the dataset. Created by the script and not committed |
| `models/` | Trained model output. Not committed |

## Environment variables
The script reads Spaces credentials from the environment. They are never stored in the repo.

| Variable | Meaning |
|---|---|
| `DO_SPACES_ACCESS_KEY` | Spaces access key |
| `DO_SPACES_SECRET_KEY` | Spaces secret key |
| `DO_SPACES_BUCKET` | Name of the Space |
| `DO_SPACES_REGION` | Region of the Space |

On the Droplet they live in `training/.env`, which is git-ignored. Load them before running:

```bash
set -a; source .env; set +a
```

## Run it (on the Droplet)

```bash
git clone https://github.com/drewtomey/mis547-group4-project.git
cd mis547-group4-project/training

sudo apt update && sudo apt install -y python3-venv libgomp1
python3 -m venv fraud-env
source fraud-env/bin/activate
pip install -r requirements.txt

# create .env with the four variables above, then:
set -a; source .env; set +a
python train_fraud_model.py
```

Expected output: the class balance, the post-SMOTE balance, training times, classification reports for both models, then `Saved model artifact to models/xgb_fraud_v1.joblib` and `Uploaded model artifact to Team 4 Spaces`.

On macOS, XGBoost needs the OpenMP library: `brew install libomp`.

## Latest results

Trained on a Droplet, evaluated on the held-out 20% test set:

| Model | Precision (fraud) | Recall (fraud) | AUPRC | Training time |
|---|---|---|---|---|
| Logistic Regression (baseline) | 0.114 | 0.898 | 0.729 | 101 s |
| XGBoost (deployed) | 0.771 | 0.857 | 0.878 | 13 s |

Logistic Regression catches most fraud but flags far too many legitimate transactions, which is why XGBoost is the deployed model. Its convergence warnings during training are expected and do not affect the XGBoost model.

## Notes

- The script always pulls the dataset from the team's Space, so running it elsewhere requires access to that Space. To reproduce it independently, download `creditcard.csv` from [Kaggle](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud), upload it to your own Space at `raw_data/creditcard.csv`, and set the four variables to point at that Space.
- To deploy a newly trained model, follow "Updating the model" in [`../api/README.md`](../api/README.md).
