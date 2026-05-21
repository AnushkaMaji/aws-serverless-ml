import json
import pickle
import numpy as np
import boto3
import os

# Load model from S3 (cached after first load)
model = None

def load_model():
    global model
    if model is None:
        s3 = boto3.client("s3")
        bucket = os.environ.get("MODEL_BUCKET", "anushka-fraud-model-bucket")
        key = os.environ.get("MODEL_KEY", "models/fraud_model.pkl")
        
        print(f"Loading model from s3://{bucket}/{key}")
        s3.download_file(bucket, key, "/tmp/fraud_model.pkl")
        
        with open("/tmp/fraud_model.pkl", "rb") as f:
            model = pickle.load(f)
        print("Model loaded successfully")
    return model

def lambda_handler(event, context):
    try:
        # Parse request body
        if isinstance(event.get("body"), str):
            body = json.loads(event["body"])
        else:
            body = event.get("body", event)
        
        # Get features from request
        features = body.get("features")
        if not features:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'features' in request body"})
            }
        
        # Load model and predict
        clf = load_model()
        features_array = np.array(features).reshape(1, -1)
        prediction = clf.predict(features_array)[0]
        probability = clf.predict_proba(features_array)[0].tolist()
        
        result = {
            "prediction": int(prediction),
            "label": "FRAUD" if prediction == 1 else "LEGITIMATE",
            "fraud_probability": round(probability[1], 4),
            "legitimate_probability": round(probability[0], 4)
        }
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result)
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }