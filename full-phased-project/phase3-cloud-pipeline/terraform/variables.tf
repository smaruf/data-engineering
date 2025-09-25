# Terraform Variables for Phase 3 Cloud Pipeline Infrastructure
# ============================================================

# Project Configuration
variable "project_name" {
  description = "Name of the project for resource naming and tagging"
  type        = string
  default     = "covid-data-pipeline"
  
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "Project name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "aws_region" {
  description = "AWS region for resource deployment"
  type        = string
  default     = "us-east-1"
}

# S3 Configuration
variable "raw_data_bucket_prefix" {
  description = "Prefix for raw data S3 bucket name"
  type        = string
  default     = "covid-raw-data"
}

variable "processed_data_bucket_prefix" {
  description = "Prefix for processed data S3 bucket name"
  type        = string
  default     = "covid-processed-data"
}

variable "enable_s3_versioning" {
  description = "Enable S3 bucket versioning"
  type        = bool
  default     = true
}

variable "enable_s3_encryption" {
  description = "Enable S3 server-side encryption"
  type        = bool
  default     = true
}

# AWS Glue Configuration
variable "glue_job_name" {
  description = "Name of the AWS Glue job"
  type        = string
  default     = "covid-data-etl"
}

variable "glue_job_max_capacity" {
  description = "Maximum number of AWS Glue data processing units (DPUs)"
  type        = number
  default     = 2.0
  
  validation {
    condition     = var.glue_job_max_capacity >= 0.0625 && var.glue_job_max_capacity <= 100
    error_message = "Glue job max capacity must be between 0.0625 and 100 DPUs."
  }
}

variable "glue_job_timeout_minutes" {
  description = "Timeout for the Glue job in minutes"
  type        = number
  default     = 60
  
  validation {
    condition     = var.glue_job_timeout_minutes >= 1 && var.glue_job_timeout_minutes <= 2880
    error_message = "Glue job timeout must be between 1 and 2880 minutes."
  }
}

variable "enable_glue_dev_endpoint" {
  description = "Enable Glue development endpoint for interactive development"
  type        = bool
  default     = false
}

variable "enable_glue_encryption" {
  description = "Enable encryption for Glue job data"
  type        = bool
  default     = true
}

# Redshift Configuration (Optional)
variable "enable_redshift" {
  description = "Whether to create Redshift cluster for data warehousing"
  type        = bool
  default     = false
}

variable "redshift_node_type" {
  description = "Redshift node type"
  type        = string
  default     = "dc2.large"
  
  validation {
    condition = contains([
      "dc2.large", "dc2.8xlarge", "ds2.xlarge", "ds2.8xlarge",
      "ra3.xlplus", "ra3.4xlarge", "ra3.16xlarge"
    ], var.redshift_node_type)
    error_message = "Invalid Redshift node type."
  }
}

variable "redshift_cluster_type" {
  description = "Redshift cluster type (single-node or multi-node)"
  type        = string
  default     = "single-node"
  
  validation {
    condition     = contains(["single-node", "multi-node"], var.redshift_cluster_type)
    error_message = "Redshift cluster type must be either 'single-node' or 'multi-node'."
  }
}

variable "redshift_number_of_nodes" {
  description = "Number of nodes in the Redshift cluster (only for multi-node)"
  type        = number
  default     = 1
  
  validation {
    condition     = var.redshift_number_of_nodes >= 1 && var.redshift_number_of_nodes <= 128
    error_message = "Number of Redshift nodes must be between 1 and 128."
  }
}

variable "redshift_database_name" {
  description = "Name of the Redshift database"
  type        = string
  default     = "covid_warehouse"
  
  validation {
    condition     = can(regex("^[a-z][a-z0-9_]*$", var.redshift_database_name))
    error_message = "Redshift database name must start with a letter and contain only lowercase letters, numbers, and underscores."
  }
}

variable "redshift_master_username" {
  description = "Master username for Redshift cluster"
  type        = string
  default     = "admin"
  sensitive   = true
}

variable "redshift_master_password" {
  description = "Master password for Redshift cluster"
  type        = string
  default     = ""
  sensitive   = true
  
  validation {
    condition     = length(var.redshift_master_password) >= 8 || var.redshift_master_password == ""
    error_message = "Redshift master password must be at least 8 characters long."
  }
}

variable "redshift_publicly_accessible" {
  description = "Whether the Redshift cluster should be publicly accessible"
  type        = bool
  default     = false
}

# Monitoring and Alerting Configuration
variable "enable_cloudwatch_logs" {
  description = "Enable CloudWatch logging for Glue jobs"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 30
  
  validation {
    condition = contains([
      1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653
    ], var.log_retention_days)
    error_message = "Invalid log retention period."
  }
}

variable "enable_cloudwatch_alarms" {
  description = "Enable CloudWatch alarms for monitoring"
  type        = bool
  default     = true
}

variable "enable_sns_notifications" {
  description = "Enable SNS notifications for pipeline events"
  type        = bool
  default     = true
}

variable "notification_email" {
  description = "Email address for SNS notifications"
  type        = string
  default     = ""
  
  validation {
    condition     = can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.notification_email)) || var.notification_email == ""
    error_message = "Must be a valid email address or empty string."
  }
}

# Lambda Configuration
variable "enable_lambda_orchestration" {
  description = "Enable Lambda functions for pipeline orchestration"
  type        = bool
  default     = false
}

# Data Processing Configuration
variable "data_quality_threshold" {
  description = "Minimum data quality score threshold (0.0 to 1.0)"
  type        = number
  default     = 0.95
  
  validation {
    condition     = var.data_quality_threshold >= 0.0 && var.data_quality_threshold <= 1.0
    error_message = "Data quality threshold must be between 0.0 and 1.0."
  }
}

variable "max_error_rate" {
  description = "Maximum acceptable error rate (0.0 to 1.0)"
  type        = number
  default     = 0.05
  
  validation {
    condition     = var.max_error_rate >= 0.0 && var.max_error_rate <= 1.0
    error_message = "Max error rate must be between 0.0 and 1.0."
  }
}

# Cost Optimization
variable "enable_cost_allocation_tags" {
  description = "Enable cost allocation tags for billing"
  type        = bool
  default     = true
}

variable "enable_s3_intelligent_tiering" {
  description = "Enable S3 Intelligent Tiering for cost optimization"
  type        = bool
  default     = true
}

# Security Configuration
variable "enable_vpc_endpoints" {
  description = "Enable VPC endpoints for secure communication"
  type        = bool
  default     = false
}

variable "vpc_id" {
  description = "VPC ID for VPC endpoints (required if enable_vpc_endpoints is true)"
  type        = string
  default     = ""
}

variable "subnet_ids" {
  description = "Subnet IDs for VPC endpoints"
  type        = list(string)
  default     = []
}

# Backup and Disaster Recovery
variable "enable_cross_region_backup" {
  description = "Enable cross-region backup for disaster recovery"
  type        = bool
  default     = false
}

variable "backup_region" {
  description = "Region for cross-region backups"
  type        = string
  default     = "us-west-2"
}