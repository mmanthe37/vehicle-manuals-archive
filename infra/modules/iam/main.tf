variable "name_prefix" {}
variable "s3_bucket" {}
variable "tags" { type = map(string) }

resource "aws_iam_role" "api" {
  name = "${var.name_prefix}-api-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
  tags = var.tags
}

resource "aws_iam_policy" "s3_read" {
  name = "${var.name_prefix}-s3-read"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:HeadObject", "s3:ListBucket"]
      Resource = ["arn:aws:s3:::${var.s3_bucket}", "arn:aws:s3:::${var.s3_bucket}/*"]
    }]
  })
}

resource "aws_iam_policy" "s3_write" {
  name = "${var.name_prefix}-s3-write"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:PutObject", "s3:DeleteObject"]
      Resource = ["arn:aws:s3:::${var.s3_bucket}/*"]
    }]
  })
}

resource "aws_iam_role_policy_attachment" "api_s3_read" {
  role       = aws_iam_role.api.name
  policy_arn = aws_iam_policy.s3_read.arn
}

output "api_role_arn" { value = aws_iam_role.api.arn }
