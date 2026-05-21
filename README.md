# Serverless ML Fraud Detection API on AWS

A production-style serverless machine learning system that detects fraudulent transactions in real time using AWS Lambda, S3, ECR, API Gateway, and CloudWatch — fully provisioned with Terraform.

## Live API

curl -X POST https://rsp2qh4oh8.execute-api.us-east-1.amazonaws.com/prod/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [1.5, -0.3, 2.1, 0.8, -1.2, 0.5, 1.1, -0.7, 0.3, 1.8]}'

## Architecture

Client → API Gateway → Lambda → S3 (model) → JSON Response → CloudWatch

## Stack

- ML Model: scikit-learn Random Forest (97.45% accuracy)
- Model Storage: AWS S3
- Compute: AWS Lambda (Docker container image)
- Container Registry: AWS ECR
- API: AWS API Gateway
- Monitoring: AWS CloudWatch
- Infrastructure as Code: Terraform
- Containerization: Docker

## Project Structure

model/train.py        - Train and upload model to S3
lambda/handler.py     - Lambda inference function
lambda/requirements.txt
terraform/main.tf     - Full infrastructure as code
Dockerfile            - Container image definition

## Key Engineering Decisions

- Container over zip: scikit-learn + scipy exceed Lambda layer limits. Docker container images solve this cleanly.
- S3 model registry: Model stored in S3, not bundled in container. Enables model updates without rebuilds.
- Cold start caching: Model loaded once per Lambda instance and cached in memory.
- Terraform IaC: All infrastructure reproducible from a single terraform apply.

## AWS Services Used

- Lambda: Serverless compute, scales to zero
- S3: Model artifact storage
- ECR: Private Docker registry
- API Gateway: HTTP API routing
- CloudWatch: Metrics and error alerting
- IAM: Least-privilege execution roles
