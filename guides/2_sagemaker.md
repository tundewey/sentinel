# Guide 2 - SageMaker Embedding Endpoint

## Objective
Deploy serverless embeddings endpoint for optional semantic incident retrieval.

## Steps
```bash
cd terraform/2_sagemaker
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply
```

## Save Outputs
Add to `.env`:
- `SAGEMAKER_ENDPOINT`

## Verify
```bash
aws sagemaker describe-endpoint --endpoint-name sentinel-embedding-endpoint
```

## Next
Continue to [3_ingestion.md](3_ingestion.md).
