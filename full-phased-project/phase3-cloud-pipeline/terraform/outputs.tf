# Output values for Phase 3 Cloud Pipeline Infrastructure
# ====================================================

# S3 Bucket Outputs
output "raw_data_bucket_name" {
  description = "Name of the S3 bucket for raw data storage"
  value       = aws_s3_bucket.raw_data.bucket
}

output "raw_data_bucket_arn" {
  description = "ARN of the S3 bucket for raw data storage"
  value       = aws_s3_bucket.raw_data.arn
}

output "processed_data_bucket_name" {
  description = "Name of the S3 bucket for processed data storage"
  value       = aws_s3_bucket.processed_data.bucket
}

output "processed_data_bucket_arn" {
  description = "ARN of the S3 bucket for processed data storage"
  value       = aws_s3_bucket.processed_data.arn
}

output "logs_bucket_name" {
  description = "Name of the S3 bucket for application logs"
  value       = aws_s3_bucket.logs.bucket
}

output "logs_bucket_arn" {
  description = "ARN of the S3 bucket for application logs"
  value       = aws_s3_bucket.logs.arn
}

# AWS Glue Outputs
output "glue_database_name" {
  description = "Name of the AWS Glue catalog database"
  value       = aws_glue_catalog_database.covid_database.name
}

output "glue_job_name" {
  description = "Name of the AWS Glue ETL job"
  value       = aws_glue_job.covid_etl_job.name
}

output "glue_job_arn" {
  description = "ARN of the AWS Glue ETL job"
  value       = aws_glue_job.covid_etl_job.arn
}

output "glue_job_role_arn" {
  description = "ARN of the IAM role for Glue jobs"
  value       = aws_iam_role.glue_job_role.arn
}

# Redshift Outputs (if enabled)
output "redshift_cluster_identifier" {
  description = "Redshift cluster identifier (if enabled)"
  value       = var.enable_redshift ? aws_redshift_cluster.covid_warehouse[0].cluster_identifier : null
}

output "redshift_cluster_endpoint" {
  description = "Redshift cluster endpoint (if enabled)"
  value       = var.enable_redshift ? aws_redshift_cluster.covid_warehouse[0].endpoint : null
}

output "redshift_cluster_port" {
  description = "Redshift cluster port (if enabled)"
  value       = var.enable_redshift ? aws_redshift_cluster.covid_warehouse[0].port : null
}

output "redshift_database_name" {
  description = "Redshift database name (if enabled)"
  value       = var.enable_redshift ? aws_redshift_cluster.covid_warehouse[0].database_name : null
}

# Monitoring Outputs
output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group for Glue jobs"
  value       = aws_cloudwatch_log_group.glue_job_logs.name
}

output "cloudwatch_log_group_arn" {
  description = "ARN of the CloudWatch log group for Glue jobs"
  value       = aws_cloudwatch_log_group.glue_job_logs.arn
}

output "sns_topic_arn" {
  description = "ARN of the SNS topic for notifications (if enabled)"
  value       = var.enable_sns_notifications ? aws_sns_topic.pipeline_notifications[0].arn : null
}

# Lambda Outputs (if enabled)
output "lambda_function_name" {
  description = "Name of the Lambda orchestrator function (if enabled)"
  value       = var.enable_lambda_orchestration ? aws_lambda_function.pipeline_orchestrator[0].function_name : null
}

output "lambda_function_arn" {
  description = "ARN of the Lambda orchestrator function (if enabled)"
  value       = var.enable_lambda_orchestration ? aws_lambda_function.pipeline_orchestrator[0].arn : null
}

# Environment Configuration Outputs
output "aws_region" {
  description = "AWS region where resources are deployed"
  value       = var.aws_region
}

output "project_name" {
  description = "Project name used for resource naming"
  value       = var.project_name
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}

# Security Outputs
output "glue_security_configuration_name" {
  description = "Name of the Glue security configuration (if enabled)"
  value       = var.enable_glue_encryption ? aws_glue_security_configuration.etl_security[0].name : null
}

# Resource URLs and Endpoints
output "s3_console_urls" {
  description = "AWS Console URLs for S3 buckets"
  value = {
    raw_data      = "https://s3.console.aws.amazon.com/s3/buckets/${aws_s3_bucket.raw_data.bucket}"
    processed_data = "https://s3.console.aws.amazon.com/s3/buckets/${aws_s3_bucket.processed_data.bucket}"
    logs          = "https://s3.console.aws.amazon.com/s3/buckets/${aws_s3_bucket.logs.bucket}"
  }
}

output "glue_console_url" {
  description = "AWS Console URL for Glue job"
  value       = "https://${var.aws_region}.console.aws.amazon.com/glue/home?region=${var.aws_region}#etl:tab=jobs"
}

output "cloudwatch_console_url" {
  description = "AWS Console URL for CloudWatch logs"
  value       = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#logsV2:log-groups/log-group/${replace(aws_cloudwatch_log_group.glue_job_logs.name, "/", "$252F")}"
}

# Data Pipeline Configuration
output "pipeline_configuration" {
  description = "Configuration values for the data pipeline"
  value = {
    input_s3_path  = "s3://${aws_s3_bucket.raw_data.bucket}/covid-data/"
    output_s3_path = "s3://${aws_s3_bucket.processed_data.bucket}/covid-processed/"
    database_name  = aws_glue_catalog_database.covid_database.name
    table_name     = "covid_processed"
    job_name       = aws_glue_job.covid_etl_job.name
  }
}

# Cost Tracking
output "resource_tags" {
  description = "Common tags applied to all resources for cost tracking"
  value = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Owner       = "DataEngineering"
  }
}