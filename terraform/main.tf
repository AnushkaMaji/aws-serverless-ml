terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# S3 bucket for model storage
resource "aws_s3_bucket" "model_bucket" {
  bucket = "anushka-fraud-model-bucket"
}

# ECR repository for Docker image
resource "aws_ecr_repository" "fraud_detector" {
  name = "fraud-detector"
}

# IAM role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "fraud-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "s3_access" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "cloudwatch_access" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

# Lambda function
resource "aws_lambda_function" "fraud_detector" {
  function_name = "fraud-detector"
  role          = aws_iam_role.lambda_role.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.fraud_detector.repository_url}:latest"
  timeout       = 30
  memory_size   = 512

  environment {
    variables = {
      MODEL_BUCKET = aws_s3_bucket.model_bucket.bucket
      MODEL_KEY    = "models/fraud_model.pkl"
    }
  }
}

# API Gateway
resource "aws_apigatewayv2_api" "fraud_api" {
  name          = "fraud-detector-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id             = aws_apigatewayv2_api.fraud_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.fraud_detector.arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "predict_route" {
  api_id    = aws_apigatewayv2_api.fraud_api.id
  route_key = "POST /predict"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_stage" "prod" {
  api_id      = aws_apigatewayv2_api.fraud_api.id
  name        = "prod"
  auto_deploy = true
}

# CloudWatch alarm
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "fraud-detector-errors"
  alarm_description   = "Alert when fraud detector Lambda has errors"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  statistic           = "Sum"
  period              = 60
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.fraud_detector.function_name
  }
}

# Output the API URL
output "api_url" {
  value = "${aws_apigatewayv2_stage.prod.invoke_url}/predict"
}