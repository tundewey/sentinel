# Guide 1 - AWS Permissions Setup

## Objective
Grant minimum permissions required to deploy Sentinel stages 2-8.

## Required Policies
Attach these to your Sentinel IAM group/user:
- `AmazonSageMakerFullAccess`
- `AmazonBedrockFullAccess`
- `AWSLambda_FullAccess`
- `AmazonAPIGatewayAdministrator`
- `AmazonRDSDataFullAccess`
- `AmazonSQSFullAccess`
- `AmazonEventBridgeFullAccess`
- `CloudWatchFullAccess`
- `AmazonS3FullAccess`
- `AWSAppRunnerFullAccess`
- `SecretsManagerReadWrite`

## Verify
```bash
aws sts get-caller-identity
aws lambda list-functions --max-items 5
aws rds describe-db-clusters
```

## Next
Continue to [2_sagemaker.md](2_sagemaker.md).
