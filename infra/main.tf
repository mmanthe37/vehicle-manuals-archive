terraform {
  required_version = ">= 1.8"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.50"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  default = "us-east-1"
}

variable "environment" {
  default = "dev"
}

variable "project" {
  default = "vmw"
}

locals {
  name_prefix = "${var.project}-${var.environment}"
  common_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

module "network" {
  source      = "./modules/network"
  name_prefix = local.name_prefix
  tags        = local.common_tags
}

module "kms" {
  source      = "./modules/kms"
  name_prefix = local.name_prefix
  tags        = local.common_tags
}

module "s3" {
  source      = "./modules/s3"
  name_prefix = local.name_prefix
  kms_key_arn = module.kms.key_arn
  tags        = local.common_tags
}

module "rds" {
  source            = "./modules/rds"
  name_prefix       = local.name_prefix
  vpc_id            = module.network.vpc_id
  subnet_ids        = module.network.private_subnet_ids
  security_group_ids = [module.network.db_security_group_id]
  kms_key_arn       = module.kms.key_arn
  tags              = local.common_tags
}

module "opensearch" {
  source            = "./modules/opensearch"
  name_prefix       = local.name_prefix
  vpc_id            = module.network.vpc_id
  subnet_ids        = module.network.private_subnet_ids
  security_group_ids = [module.network.opensearch_security_group_id]
  kms_key_id        = module.kms.key_id
  tags              = local.common_tags
}

module "iam" {
  source      = "./modules/iam"
  name_prefix = local.name_prefix
  s3_bucket   = module.s3.bucket_name
  tags        = local.common_tags
}

module "ecr" {
  source      = "./modules/ecr"
  name_prefix = local.name_prefix
  services    = ["api", "worker-ingest", "worker-parse", "worker-index"]
  tags        = local.common_tags
}

output "s3_bucket" {
  value = module.s3.bucket_name
}

output "rds_endpoint" {
  value     = module.rds.endpoint
  sensitive = true
}

output "opensearch_endpoint" {
  value = module.opensearch.endpoint
}

output "ecr_registry" {
  value = module.ecr.registry_url
}
