variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "service_name" {
  type    = string
  default = "sentinel-intel"
}

variable "ecr_repo_name" {
  type    = string
  default = "sentinel-intel"
}

variable "image_identifier" {
  type        = string
  description = "ECR image URI with tag, e.g. 123456789012.dkr.ecr.us-east-1.amazonaws.com/sentinel-intel:latest"
}

variable "bedrock_region" {
  type    = string
  default = "us-east-1"
}

variable "support_model_id" {
  type    = string
  default = "openai.gpt-oss-120b-1:0"
}
