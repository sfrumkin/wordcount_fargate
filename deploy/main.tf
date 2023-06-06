terraform {
  backend "s3" {
    bucket         = "word-fargate-tfstate"
    key            = "word-fargate-tfstate.tfstate"
    region         = "eu-west-1"
    encrypt        = true
    dynamodb_table = "wordcount-fargate-tf-state-lock"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.67.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5.1"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.3.0"
    }
  }

  required_version = "~> 1.4"
}

provider "aws" {
  region = var.aws_region
}

locals {
  prefix = "${var.prefix}-${terraform.workspace}"
  common_tags = {
    ApplicationName = var.ApplicationName
    Environment     = terraform.workspace
    ManagedBy       = "Terraform"
  }

  only_in_dev_mapping = {
    dev     = 1
    default = 0
    prod    = 0
  }
  only_in_dev = local.only_in_dev_mapping[terraform.workspace]
}
resource "random_pet" "lambda_bucket_name" {
  prefix = "wordcount-sf"
  length = 4
}

