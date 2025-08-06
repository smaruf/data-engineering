# AWS Infrastructure Setup for Week 3 Cloud ETL Pipeline
# =====================================================
# This Terraform configuration creates the necessary AWS resources for the serverless data pipeline:
# - S3 bucket for data storage
# - Redshift cluster for data warehousing (optional)
# - IAM roles and policies for Glue jobs

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project for resource tagging"
  type        = string
  default     = "week3-cloud-etl"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "enable_redshift" {
  description = "Whether to create Redshift cluster"
  type        = bool
  default     = false
}

# S3 Bucket for Raw Data
resource "aws_s3_bucket" "covid_raw_data" {
  bucket = "${var.project_name}-raw-data-${var.environment}-${random_string.bucket_suffix.result}"

  tags = {
    Name        = "COVID Raw Data Bucket"
    Project     = var.project_name
    Environment = var.environment
  }
}

# S3 Bucket for Processed Data
resource "aws_s3_bucket" "covid_processed_data" {
  bucket = "${var.project_name}-processed-data-${var.environment}-${random_string.bucket_suffix.result}"

  tags = {
    Name        = "COVID Processed Data Bucket"
    Project     = var.project_name
    Environment = var.environment
  }
}

# Random string for unique bucket naming
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# S3 Bucket versioning for raw data
resource "aws_s3_bucket_versioning" "covid_raw_data_versioning" {
  bucket = aws_s3_bucket.covid_raw_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Bucket versioning for processed data
resource "aws_s3_bucket_versioning" "covid_processed_data_versioning" {
  bucket = aws_s3_bucket.covid_processed_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Bucket public access block (security best practice)
resource "aws_s3_bucket_public_access_block" "covid_raw_data_pab" {
  bucket = aws_s3_bucket.covid_raw_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "covid_processed_data_pab" {
  bucket = aws_s3_bucket.covid_processed_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# IAM Role for Glue Jobs
resource "aws_iam_role" "glue_job_role" {
  name = "${var.project_name}-glue-job-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "Glue Job Role"
    Project     = var.project_name
    Environment = var.environment
  }
}

# Attach AWS managed policy for Glue service
resource "aws_iam_role_policy_attachment" "glue_service_role" {
  role       = aws_iam_role.glue_job_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# IAM Policy for S3 access
resource "aws_iam_role_policy" "glue_s3_policy" {
  name = "${var.project_name}-glue-s3-policy-${var.environment}"
  role = aws_iam_role.glue_job_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.covid_raw_data.arn,
          "${aws_s3_bucket.covid_raw_data.arn}/*",
          aws_s3_bucket.covid_processed_data.arn,
          "${aws_s3_bucket.covid_processed_data.arn}/*"
        ]
      }
    ]
  })
}

# Optional: Redshift Cluster
resource "aws_redshift_cluster" "covid_warehouse" {
  count = var.enable_redshift ? 1 : 0

  cluster_identifier = "${var.project_name}-redshift-${var.environment}"
  database_name      = "covid_warehouse"
  master_username    = "admin"
  master_password    = "TempPassword123!" # In production, use AWS Secrets Manager
  
  node_type       = "dc2.large"
  cluster_type    = "single-node"
  
  publicly_accessible = false
  encrypted          = true
  
  skip_final_snapshot = true # For dev environment only

  tags = {
    Name        = "COVID Data Warehouse"
    Project     = var.project_name
    Environment = var.environment
  }
}

# Outputs
output "raw_data_bucket_name" {
  description = "Name of the S3 bucket for raw data"
  value       = aws_s3_bucket.covid_raw_data.bucket
}

output "processed_data_bucket_name" {
  description = "Name of the S3 bucket for processed data"
  value       = aws_s3_bucket.covid_processed_data.bucket
}

output "glue_job_role_arn" {
  description = "ARN of the IAM role for Glue jobs"
  value       = aws_iam_role.glue_job_role.arn
}

output "redshift_cluster_endpoint" {
  description = "Redshift cluster endpoint (if enabled)"
  value       = var.enable_redshift ? aws_redshift_cluster.covid_warehouse[0].endpoint : null
}