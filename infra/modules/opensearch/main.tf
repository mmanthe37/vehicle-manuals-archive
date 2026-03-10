variable "name_prefix" {}
variable "vpc_id" {}
variable "subnet_ids" { type = list(string) }
variable "security_group_ids" { type = list(string) }
variable "kms_key_id" {}
variable "tags" { type = map(string) }

resource "aws_opensearch_domain" "main" {
  domain_name    = "${var.name_prefix}-os"
  engine_version = "OpenSearch_2.13"

  cluster_config {
    instance_type  = "t3.medium.search"
    instance_count = 2
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 100
    volume_type = "gp3"
  }

  vpc_options {
    subnet_ids         = [var.subnet_ids[0]]
    security_group_ids = var.security_group_ids
  }

  encrypt_at_rest { enabled = true; kms_key_id = var.kms_key_id }
  node_to_node_encryption { enabled = true }
  domain_endpoint_options { enforce_https = true }

  tags = var.tags
}

output "endpoint" { value = aws_opensearch_domain.main.endpoint }
output "domain_arn" { value = aws_opensearch_domain.main.arn }
