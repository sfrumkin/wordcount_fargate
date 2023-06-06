# Input variable definitions

variable "aws_region" {
  description = "AWS region for all resources."

  type    = string
  default = "eu-west-1"
}

variable "ApplicationName" {
  default = "wordcount"
}

variable "prefix" {
  default = "sf"
}
