variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "frontend_bucket_name" {
  type = string
}

variable "api_lambda_zip" {
  type    = string
  default = "../../backend/api/api_lambda.zip"
}

variable "api_lambda_name" {
  type    = string
  default = "sentinel-api"
}
