variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "planner_lambda_name" {
  type    = string
  default = "sentinel-planner"
}

variable "api_lambda_name" {
  type    = string
  default = "sentinel-api"
}

variable "sqs_queue_name" {
  type    = string
  default = "sentinel-analysis-jobs"
}

variable "alarm_email" {
  type    = string
  default = ""
}
