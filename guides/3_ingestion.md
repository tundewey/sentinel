# Guide 3 - Incident Ingestion Pipeline

## Objective
Deploy ingest Lambda + API Gateway endpoint for incident intake.

## Build Package
```bash
cd backend/ingest
uv run package.py
```

## Deploy Infra
```bash
cd ../../terraform/3_ingestion
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply
```

## Save Outputs
Add to `.env`:
- `SENTINEL_INGEST_API_ENDPOINT`
- `SENTINEL_INGEST_API_KEY`

## Verify
```bash
cd ../../backend/ingest
uv run test_ingest.py
```

## Next
Continue to [4_intel.md](4_intel.md).
