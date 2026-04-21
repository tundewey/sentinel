# Guide 4 - Intel Service (App Runner)

## Objective
Deploy App Runner service for supporting LLM-assisted context analysis.

## Model Guidance
- Supporting analysis model: `openai.gpt-oss-120b-1:0`
- Bedrock region should match model availability.

## Build and Push Image
```bash
cd backend/intel
# Build/push image with your ECR URL
```

## Deploy Infra
```bash
cd ../../terraform/4_intel
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply
```

## Save Outputs
Add to `.env`:
- `SENTINEL_INTEL_URL`

## Verify
```bash
cd ../../backend/intel
uv run test_intel.py
```

## Next
Continue to [5_database.md](5_database.md).
