output "aurora_cluster_arn" {
  value = aws_rds_cluster.aurora.arn
}

output "aurora_secret_arn" {
  value = aws_secretsmanager_secret.aurora.arn
}

output "aurora_cluster_endpoint" {
  value = aws_rds_cluster.aurora.endpoint
}
