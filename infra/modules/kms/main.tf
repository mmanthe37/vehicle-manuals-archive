variable "name_prefix" {}
variable "tags" { type = map(string) }

resource "aws_kms_key" "main" {
  description             = "${var.name_prefix} encryption key"
  enable_key_rotation     = true
  deletion_window_in_days = 30
  tags                    = var.tags
}

resource "aws_kms_alias" "main" {
  name          = "alias/${var.name_prefix}"
  target_key_id = aws_kms_key.main.key_id
}

output "key_id"  { value = aws_kms_key.main.key_id }
output "key_arn" { value = aws_kms_key.main.arn }
