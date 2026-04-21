output "sqs_queue_url" {
  value = aws_sqs_queue.jobs.id
}

output "sqs_queue_arn" {
  value = aws_sqs_queue.jobs.arn
}

output "agent_lambda_names" {
  value = [for f in aws_lambda_function.agents : f.function_name]
}
