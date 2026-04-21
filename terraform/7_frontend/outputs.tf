output "cloudfront_url" {
  value = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "api_gateway_url" {
  value = aws_apigatewayv2_stage.default.invoke_url
}

output "frontend_bucket" {
  value = aws_s3_bucket.frontend.bucket
}
