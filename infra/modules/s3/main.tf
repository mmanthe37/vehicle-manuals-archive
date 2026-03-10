variable "name_prefix" {}
variable "kms_key_arn" {}
variable "tags" { type = map(string) }

resource "aws_s3_bucket" "manuals" {
  bucket = "${var.name_prefix}-oem-manuals"
  tags   = var.tags
}

resource "aws_s3_bucket_versioning" "manuals" {
  bucket = aws_s3_bucket.manuals.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "manuals" {
  bucket = aws_s3_bucket.manuals.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.kms_key_arn
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "manuals" {
  bucket = aws_s3_bucket.manuals.id
  rule {
    id     = "tiered-storage"
    status = "Enabled"
    transition { days = 90; storage_class = "STANDARD_IA" }
    transition { days = 365; storage_class = "GLACIER_IR" }
  }
}

resource "aws_s3_bucket_public_access_block" "manuals" {
  bucket                  = aws_s3_bucket.manuals.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

output "bucket_name" { value = aws_s3_bucket.manuals.id }
output "bucket_arn"  { value = aws_s3_bucket.manuals.arn }
