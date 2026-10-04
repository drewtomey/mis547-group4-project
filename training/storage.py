# Group 4
# MIS 547
# Name: training/storage.py
# v1.1
# This script automatically saves the model file to DigitalOcean Spaces.
# Original Dataset: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud
# Reference: https://docs.digitalocean.com/products/spaces/reference/aws-sdks/

import os
import boto3
from dotenv import load_dotenv

# load credentials from .env
load_dotenv()

SPACES_KEY = os.getenv("SPACES_ACCESS_KEY")
SPACES_SECRET = os.getenv("SPACES_SECRET_KEY")
SPACES_ENDPOINT = os.getenv("SPACES_ENDPOINT", "https://sfo3.digitaloceanspaces.com")
SPACES_REGION = os.getenv("SPACES_REGION", "nyc3")
SPACES_BUCKET = os.getenv("SPACES_BUCKET", "mis547-group4-space")


# initializes a boto3 client
def get_spaces_client():
    session = boto3.session.Session()
    client = session.client(
        "s3",
        region_name=SPACES_REGION,
        endpoint_url=SPACES_ENDPOINT,
        aws_access_key_id=SPACES_KEY,
        aws_secret_access_key=SPACES_SECRET,
    )
    return client

# uploads a local file to your DigitalOcean Space.
def upload_to_space(local_file_path: str, remote_key: str) -> None:
    client = get_spaces_client()
    client.upload_file(
        Filename=local_file_path,
        Bucket=SPACES_BUCKET,
        Key=remote_key,
        ExtraArgs={"ACL": "private"},
    )
    print(f"[Spaces] Uploaded '{local_file_path}' -> 's3://{SPACES_BUCKET}/{remote_key}'")

# downloads a file from your DigitalOcean Space to a local path.
def download_from_space(remote_key: str, local_destination_path: str) -> None:
    client = get_spaces_client()
    client.download_file(
        Bucket=SPACES_BUCKET,
        Key=remote_key,
        Filename=local_destination_path,
    )
    print(f"[Spaces] Downloaded 's3://{SPACES_BUCKET}/{remote_key}' -> '{local_destination_path}'")