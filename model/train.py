import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle
import boto3
import os

# Generate synthetic fraud detection data
print("Generating training data...")
X, y = make_classification(
    n_samples=10000,
    n_features=10,
    n_informative=6,
    n_redundant=2,
    random_state=42,
    weights=[0.95, 0.05]  # 5% fraud rate, realistic imbalance
)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
print("Training Random Forest model...")
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    class_weight='balanced'
)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model accuracy: {accuracy:.4f}")

# Save model locally
os.makedirs("model", exist_ok=True)
with open("model/fraud_model.pkl", "wb") as f:
    pickle.dump(model, f)
print("Model saved locally to model/fraud_model.pkl")

# Upload to S3
BUCKET_NAME = "anushka-fraud-model-bucket"
s3 = boto3.client("s3", region_name="us-east-1")

# Create bucket if it doesn't exist
try:
    s3.create_bucket(Bucket=BUCKET_NAME)
    print(f"Created S3 bucket: {BUCKET_NAME}")
except s3.exceptions.BucketAlreadyOwnedByYou:
    print(f"Bucket already exists: {BUCKET_NAME}")

# Upload model
s3.upload_file("model/fraud_model.pkl", BUCKET_NAME, "models/fraud_model.pkl")
print(f"Model uploaded to s3://{BUCKET_NAME}/models/fraud_model.pkl")