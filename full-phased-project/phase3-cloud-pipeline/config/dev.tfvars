# Development Environment Configuration for Phase 3 Cloud Pipeline
# ===============================================================

# Project Configuration
project_name = "covid-data-pipeline"
environment  = "dev"
aws_region   = "us-east-1"

# S3 Configuration
raw_data_bucket_prefix      = "covid-raw-data"
processed_data_bucket_prefix = "covid-processed-data"
enable_s3_versioning        = true
enable_s3_encryption        = true
enable_s3_intelligent_tiering = true

# AWS Glue Configuration
glue_job_name               = "covid-data-etl-dev"
glue_job_max_capacity       = 2.0      # Start small for dev
glue_job_timeout_minutes    = 30       # Shorter timeout for dev
enable_glue_dev_endpoint    = false    # Keep disabled for cost
enable_glue_encryption      = true

# Redshift Configuration (Disabled for dev to save costs)
enable_redshift             = false
redshift_node_type          = "dc2.large"
redshift_cluster_type       = "single-node"
redshift_database_name      = "covid_warehouse_dev"
redshift_publicly_accessible = false

# Monitoring Configuration
enable_cloudwatch_logs      = true
log_retention_days          = 7        # Shorter retention for dev
enable_cloudwatch_alarms    = true
enable_sns_notifications    = true
notification_email          = "devteam@example.com"

# Lambda Configuration
enable_lambda_orchestration = false    # Keep disabled for simplicity in dev

# Data Processing Configuration
data_quality_threshold      = 0.90     # Slightly lower for dev
max_error_rate             = 0.10      # Higher tolerance for dev

# Cost Optimization
enable_cost_allocation_tags = true

# Security Configuration
enable_vpc_endpoints        = false    # Keep disabled for dev simplicity
vpc_id                     = ""
subnet_ids                 = []

# Backup and Disaster Recovery
enable_cross_region_backup  = false    # Not needed for dev
backup_region              = "us-west-2"