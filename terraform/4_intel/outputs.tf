output "intel_service_url" {
  value = aws_apprunner_service.intel.service_url
}

output "intel_ecr_repository_url" {
  value = aws_ecr_repository.intel.repository_url
}
