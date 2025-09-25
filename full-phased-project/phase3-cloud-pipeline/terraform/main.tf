# Enhanced AWS Infrastructure Setup for Phase 3 Cloud ETL Pipeline
# ===============================================================
# This Terraform configuration creates a complete serverless data pipeline infrastructure:
# - S3 buckets for data lake storage with lifecycle policies
# - AWS Glue jobs and data catalog for ETL processing
# - Redshift cluster for data warehousing (optional)
# - IAM roles and policies with least privilege access
# - CloudWatch monitoring and SNS notifications
# - Lambda functions for pipeline orchestration

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "DataEngineering"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Random string for unique resource naming
resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

# Local values for computed names
locals {
  account_id = data.aws_caller_identity.current.account_id
  region     = data.aws_region.current.name
  
  # Resource naming
  raw_bucket_name       = "${var.project_name}-raw-data-${var.environment}-${random_string.suffix.result}"
  processed_bucket_name = "${var.project_name}-processed-data-${var.environment}-${random_string.suffix.result}"
  logs_bucket_name      = "${var.project_name}-logs-${var.environment}-${random_string.suffix.result}"
  
  # Common tags
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Owner       = "DataEngineering"
  }
}

# S3 Bucket for Raw Data
resource "aws_s3_bucket" "raw_data" {
  bucket = local.raw_bucket_name
  tags   = local.common_tags
}

# S3 Bucket for Processed Data
resource "aws_s3_bucket" "processed_data" {
  bucket = local.processed_bucket_name
  tags   = local.common_tags
}

# S3 Bucket for Application Logs
resource "aws_s3_bucket" "logs" {
  bucket = local.logs_bucket_name
  tags   = local.common_tags
}

# S3 Bucket Versioning
resource "aws_s3_bucket_versioning" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id
  versioning_configuration {
    status = var.enable_s3_versioning ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_versioning" "processed_data" {
  bucket = aws_s3_bucket.processed_data.id
  versioning_configuration {
    status = var.enable_s3_versioning ? "Enabled" : "Suspended"
  }
}

# S3 Bucket Encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = var.enable_s3_encryption ? "AES256" : null
    }
    bucket_key_enabled = var.enable_s3_encryption
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "processed_data" {
  bucket = aws_s3_bucket.processed_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = var.enable_s3_encryption ? "AES256" : null
    }
    bucket_key_enabled = var.enable_s3_encryption
  }
}

# S3 Bucket Public Access Block (Security Best Practice)
resource "aws_s3_bucket_public_access_block" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "processed_data" {
  bucket = aws_s3_bucket.processed_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket = aws_s3_bucket.logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Lifecycle Configuration for Cost Optimization
resource "aws_s3_bucket_lifecycle_configuration" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  rule {
    id     = "raw_data_lifecycle"
    status = "Enabled"

    # Transition to IA after 30 days
    transition {
      days          = 30
      storage_class = "STANDARD_INFREQUENT_ACCESS"
    }

    # Transition to Glacier after 90 days
    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    # Transition to Deep Archive after 365 days
    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }

    # Delete old versions after 90 days
    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "processed_data" {
  bucket = aws_s3_bucket.processed_data.id

  rule {
    id     = "processed_data_lifecycle"
    status = "Enabled"

    # Keep processed data in Standard for 60 days for frequent access
    transition {
      days          = 60
      storage_class = "STANDARD_INFREQUENT_ACCESS"
    }

    transition {
      days          = 180
      storage_class = "GLACIER"
    }

    # Delete old versions after 180 days
    noncurrent_version_expiration {
      noncurrent_days = 180
    }
  }
}

# AWS Glue Database
resource "aws_glue_catalog_database" "covid_database" {
  name        = "${var.project_name}_${var.environment}_catalog"
  description = "Data catalog for COVID-19 analytics pipeline"
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

  tags = local.common_tags
}

# Attach AWS managed policy for Glue service
resource "aws_iam_role_policy_attachment" "glue_service_role" {
  role       = aws_iam_role.glue_job_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# Custom IAM Policy for S3 and CloudWatch access
resource "aws_iam_role_policy" "glue_job_policy" {
  name = "${var.project_name}-glue-job-policy-${var.environment}"
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
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Resource = [
          aws_s3_bucket.raw_data.arn,
          "${aws_s3_bucket.raw_data.arn}/*",
          aws_s3_bucket.processed_data.arn,
          "${aws_s3_bucket.processed_data.arn}/*",
          aws_s3_bucket.logs.arn,
          "${aws_s3_bucket.logs.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws-glue/*"
      },
      {
        Effect = "Allow"
        Action = [
          "glue:GetDatabase",
          "glue:GetTable",
          "glue:GetPartitions",
          "glue:CreateTable",
          "glue:UpdateTable",
          "glue:BatchCreatePartition",
          "glue:BatchUpdatePartition"
        ]
        Resource = [
          "arn:aws:glue:${local.region}:${local.account_id}:catalog",
          "arn:aws:glue:${local.region}:${local.account_id}:database/${aws_glue_catalog_database.covid_database.name}",
          "arn:aws:glue:${local.region}:${local.account_id}:table/${aws_glue_catalog_database.covid_database.name}/*"
        ]
      }
    ]
  })
}

# AWS Glue Job
resource "aws_glue_job" "covid_etl_job" {
  name     = var.glue_job_name
  role_arn = aws_iam_role.glue_job_role.arn

  command {
    script_location = "s3://${aws_s3_bucket.processed_data.bucket}/scripts/covid_transform.py"
    python_version  = "3"
  }

  # Job configuration
  default_arguments = {
    "--job-language"                     = "python"
    "--job-bookmark-option"              = "job-bookmark-enable"
    "--TempDir"                         = "s3://${aws_s3_bucket.processed_data.bucket}/temp/"
    "--enable-metrics"                  = "true"
    "--enable-spark-ui"                 = "true"
    "--spark-event-logs-path"           = "s3://${aws_s3_bucket.logs.bucket}/spark-ui-logs/"
    "--enable-continuous-cloudwatch-log" = "true"
    "--database_name"                   = aws_glue_catalog_database.covid_database.name
    "--table_name"                      = "covid_processed"
    "--partition_keys"                  = "year,month"
    "--min_completeness"                = "0.95"
    "--max_error_rate"                  = "0.05"
  }

  # Resource allocation
  max_capacity     = var.glue_job_max_capacity
  timeout          = var.glue_job_timeout_minutes
  glue_version     = "4.0"
  max_retries      = 1
  
  # Security configuration
  security_configuration = var.enable_glue_encryption ? aws_glue_security_configuration.etl_security[0].name : null

  tags = local.common_tags
}

# Glue Security Configuration (Optional)
resource "aws_glue_security_configuration" "etl_security" {
  count = var.enable_glue_encryption ? 1 : 0
  name  = "${var.project_name}-glue-security-${var.environment}"

  encryption_configuration {
    cloudwatch_encryption {
      cloudwatch_encryption_mode = "SSE-KMS"
    }

    job_bookmarks_encryption {
      job_bookmarks_encryption_mode = "SSE-KMS"
    }

    s3_encryption {
      s3_encryption_mode = "SSE-S3"
    }
  }
}

# CloudWatch Log Group for Glue Job
resource "aws_cloudwatch_log_group" "glue_job_logs" {
  name              = "/aws-glue/jobs/${var.glue_job_name}"
  retention_in_days = var.log_retention_days
  
  tags = local.common_tags
}

# SNS Topic for Notifications
resource "aws_sns_topic" "pipeline_notifications" {
  count = var.enable_sns_notifications ? 1 : 0
  name  = "${var.project_name}-pipeline-notifications-${var.environment}"
  
  tags = local.common_tags
}

# SNS Topic Subscription
resource "aws_sns_topic_subscription" "email_notifications" {
  count     = var.enable_sns_notifications && var.notification_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.pipeline_notifications[0].arn
  protocol  = "email"
  endpoint  = var.notification_email
}

# CloudWatch Alarms for Glue Job Monitoring
resource "aws_cloudwatch_metric_alarm" "glue_job_failure" {
  count = var.enable_cloudwatch_alarms ? 1 : 0
  
  alarm_name          = "${var.project_name}-glue-job-failure-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "glue.driver.aggregate.numFailedTasks"
  namespace           = "AWS/Glue"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "This metric monitors glue job failures"
  alarm_actions       = var.enable_sns_notifications ? [aws_sns_topic.pipeline_notifications[0].arn] : []

  dimensions = {
    JobName = aws_glue_job.covid_etl_job.name
  }

  tags = local.common_tags
}

# Lambda function for pipeline orchestration (optional)
resource "aws_lambda_function" "pipeline_orchestrator" {
  count = var.enable_lambda_orchestration ? 1 : 0
  
  filename      = "lambda_orchestrator.zip"
  function_name = "${var.project_name}-pipeline-orchestrator-${var.environment}"
  role          = aws_iam_role.lambda_execution_role[0].arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  timeout       = 300

  environment {
    variables = {
      GLUE_JOB_NAME         = aws_glue_job.covid_etl_job.name
      RAW_BUCKET            = aws_s3_bucket.raw_data.bucket
      PROCESSED_BUCKET      = aws_s3_bucket.processed_data.bucket
      SNS_TOPIC_ARN         = var.enable_sns_notifications ? aws_sns_topic.pipeline_notifications[0].arn : ""
    }
  }

  tags = local.common_tags
}

# IAM Role for Lambda function
resource "aws_iam_role" "lambda_execution_role" {
  count = var.enable_lambda_orchestration ? 1 : 0
  name  = "${var.project_name}-lambda-execution-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

# Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  count      = var.enable_lambda_orchestration ? 1 : 0
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_execution_role[0].name
}

# Lambda Glue job execution policy
resource "aws_iam_role_policy" "lambda_glue_policy" {
  count = var.enable_lambda_orchestration ? 1 : 0
  name  = "${var.project_name}-lambda-glue-policy-${var.environment}"
  role  = aws_iam_role.lambda_execution_role[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "glue:StartJobRun",
          "glue:GetJobRun",
          "glue:GetJobRuns",
          "glue:BatchStopJobRun"
        ]
        Resource = aws_glue_job.covid_etl_job.arn
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = var.enable_sns_notifications ? aws_sns_topic.pipeline_notifications[0].arn : ""
      }
    ]
  })
}