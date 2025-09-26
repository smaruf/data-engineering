# Phase 3: Cloud Data Pipeline

## Overview

This phase implements a serverless data pipeline on AWS that demonstrates cloud-native data engineering practices. It processes COVID-19 data using AWS Glue with PySpark, stores data in S3, and optionally loads into Redshift for analytics.

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Raw Data  │───▶│  AWS Glue   │───▶│  Processed  │───▶│  Redshift   │
│   (S3)      │    │  ETL Job    │    │  Data (S3)  │    │(Optional)   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Features

### AWS Glue ETL
- **Serverless Processing**: No infrastructure management required
- **PySpark Integration**: Distributed data processing with Spark
- **Schema Evolution**: Handle schema changes gracefully
- **Partitioned Storage**: Efficient data organization by date
- **Data Catalog**: Automatic schema discovery and metadata management

### Infrastructure as Code
- **Terraform Configuration**: Complete infrastructure automation
- **Multi-Environment Support**: Dev, staging, and production environments
- **Security Best Practices**: IAM roles, encryption, and access controls
- **Cost Optimization**: Resource tagging and lifecycle policies

### Data Storage & Management
- **S3 Data Lake**: Scalable and cost-effective storage
- **Partitioned Parquet**: Optimized for analytics workloads
- **Data Versioning**: Track data changes over time
- **Lifecycle Policies**: Automatic data archival and cleanup

## Tech Stack

- **AWS Glue**: Serverless ETL service
- **PySpark**: Distributed data processing framework
- **Amazon S3**: Object storage for data lake
- **Amazon Redshift**: Data warehouse (optional)
- **Terraform**: Infrastructure as Code
- **Python**: Scripting and automation
- **AWS Lambda**: Serverless functions for triggers

## Project Structure

```
phase3-cloud-pipeline/
├── glue_job/
│   ├── covid_transform.py       # Main PySpark ETL script
│   ├── data_quality_checks.py   # Data quality validation
│   ├── schema_evolution.py      # Handle schema changes
│   └── utils/
│       ├── __init__.py
│       ├── transformations.py   # Common transformations
│       └── validators.py        # Data validation functions
├── terraform/
│   ├── main.tf                  # Main Terraform configuration
│   ├── variables.tf             # Variable definitions
│   ├── outputs.tf               # Output definitions
│   ├── s3.tf                    # S3 bucket resources
│   ├── glue.tf                  # Glue job and catalog
│   ├── redshift.tf              # Redshift cluster (optional)
│   ├── iam.tf                   # IAM roles and policies
│   └── monitoring.tf            # CloudWatch and SNS
├── lambda/
│   ├── trigger_glue_job.py      # Lambda to trigger Glue jobs
│   ├── data_quality_monitor.py  # Monitor data quality
│   └── s3_event_handler.py      # Handle S3 events
├── src/
│   ├── __init__.py
│   ├── pipeline_orchestrator.py # Pipeline orchestration
│   ├── data_uploader.py         # Upload data to S3
│   └── redshift_loader.py       # Load data to Redshift
├── tests/
│   ├── __init__.py
│   ├── test_glue_job.py         # Test Glue job logic
│   └── test_infrastructure.py   # Test Terraform code
├── config/
│   ├── dev.tfvars               # Development variables
│   ├── staging.tfvars           # Staging variables
│   └── prod.tfvars              # Production variables
├── scripts/
│   ├── deploy.sh                # Deployment script
│   ├── setup_sample_data.py     # Create sample data
│   └── monitor_jobs.py          # Monitor Glue jobs
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Quick Start

### Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured with credentials
3. **Terraform** v1.0+ installed
4. **Python 3.8+** with boto3
5. **Docker** (optional, for local testing)

### Installation

1. **Clone and navigate to Phase 3**:
   ```bash
   cd full-phased-project/phase3-cloud-pipeline
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure AWS credentials**:
   ```bash
   aws configure
   ```

4. **Initialize Terraform**:
   ```bash
   cd terraform
   terraform init
   ```

### Deployment

1. **Review and customize variables**:
   ```bash
   cp config/dev.tfvars.example config/dev.tfvars
   # Edit config/dev.tfvars with your settings
   ```

2. **Plan infrastructure deployment**:
   ```bash
   terraform plan -var-file=../config/dev.tfvars
   ```

3. **Deploy infrastructure**:
   ```bash
   terraform apply -var-file=../config/dev.tfvars
   ```

4. **Upload sample data**:
   ```bash
   python ../scripts/setup_sample_data.py
   ```

5. **Run Glue job**:
   ```bash
   python ../src/pipeline_orchestrator.py --job-name covid-data-etl
   ```

## Configuration

### Terraform Variables

Edit `config/dev.tfvars`:

```hcl
# Project Configuration
project_name = "covid-data-pipeline"
environment  = "dev"
aws_region   = "us-east-1"

# S3 Configuration
raw_data_bucket_prefix      = "covid-raw-data"
processed_data_bucket_prefix = "covid-processed-data"
enable_s3_versioning        = true
enable_s3_encryption        = true

# Glue Configuration
glue_job_name               = "covid-data-etl"
glue_job_max_capacity       = 2.0
glue_job_timeout_minutes    = 60
enable_glue_dev_endpoint    = false

# Redshift Configuration (Optional)
enable_redshift             = false
redshift_node_type          = "dc2.large"
redshift_cluster_type       = "single-node"
redshift_database_name      = "covid_warehouse"

# Monitoring Configuration
enable_cloudwatch_logs      = true
enable_sns_notifications    = true
notification_email          = "your-email@example.com"
```

### Environment Variables

```bash
# AWS Configuration
export AWS_REGION=us-east-1
export AWS_PROFILE=default

# Pipeline Configuration
export GLUE_JOB_NAME=covid-data-etl
export S3_RAW_BUCKET=your-raw-data-bucket
export S3_PROCESSED_BUCKET=your-processed-data-bucket

# Monitoring
export SNS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:data-pipeline-alerts
```

## Data Pipeline Components

### 1. Data Ingestion
- **Source**: COVID-19 APIs and batch files
- **Format**: CSV, JSON, Parquet
- **Storage**: S3 raw data bucket
- **Partitioning**: By date (year/month/day)

### 2. Data Processing (AWS Glue)
- **Cleaning**: Remove duplicates, handle nulls
- **Transformation**: Standardize formats, calculate metrics
- **Validation**: Data quality checks and profiling
- **Enrichment**: Add calculated fields and metadata

### 3. Data Storage
- **Format**: Parquet with Snappy compression
- **Partitioning**: By year/month for query optimization
- **Schema**: Evolving schema with backward compatibility
- **Metadata**: AWS Glue Data Catalog

### 4. Data Warehouse (Optional)
- **Redshift**: OLAP queries and analytics
- **Tables**: Fact and dimension tables
- **Views**: Business-friendly data views
- **ETL**: Scheduled data loads from S3

## AWS Glue Job Details

### Main ETL Script (`glue_job/covid_transform.py`)

The Glue job performs the following operations:

1. **Data Reading**:
   ```python
   # Read from S3 with schema inference
   df = spark.read.option("header", "true").csv(input_path)
   ```

2. **Data Cleaning**:
   ```python
   # Remove nulls and standardize formats
   df_clean = df.filter(col("country").isNotNull())
   df_clean = df_clean.withColumn("country", trim(upper(col("country"))))
   ```

3. **Data Transformation**:
   ```python
   # Add calculated fields
   df_transformed = df_clean.withColumn("year", year(col("date")))
   df_transformed = df_transformed.withColumn("case_fatality_rate", 
                                            col("deaths") / col("cases") * 100)
   ```

4. **Data Writing**:
   ```python
   # Write partitioned Parquet files
   df_transformed.write.mode("overwrite").partitionBy("year", "month").parquet(output_path)
   ```

### Data Quality Checks

Implemented data quality validations:

- **Completeness**: Check for required fields
- **Validity**: Validate data types and ranges
- **Consistency**: Cross-field validation rules
- **Freshness**: Ensure data is recent
- **Uniqueness**: Detect and handle duplicates

### Schema Evolution

Handle schema changes gracefully:

- **Backward Compatibility**: Support older data formats
- **Column Addition**: Add new columns with defaults
- **Column Removal**: Mark columns as deprecated
- **Data Type Changes**: Convert types safely

## Monitoring & Alerting

### CloudWatch Integration
- **Job Metrics**: Success rates, execution times, record counts
- **Custom Metrics**: Data quality scores, processing rates
- **Logs**: Detailed execution logs with structured logging
- **Dashboards**: Visual monitoring of pipeline health

### SNS Notifications
- **Job Success/Failure**: Email alerts for job status
- **Data Quality Issues**: Alerts for quality threshold breaches
- **Infrastructure Changes**: Notifications for resource updates
- **Cost Optimization**: Alerts for unusual spending patterns

### Monitoring Scripts

```bash
# Monitor Glue job status
python scripts/monitor_jobs.py --job-name covid-data-etl

# Check data quality metrics
python scripts/check_data_quality.py --date 2024-01-15

# View pipeline costs
python scripts/cost_analysis.py --start-date 2024-01-01
```

## Cost Optimization

### Glue Job Optimization
- **DPU Scaling**: Right-size worker capacity
- **Job Bookmarks**: Process only new data
- **Partition Pruning**: Read only required partitions
- **Compression**: Use efficient compression formats

### S3 Storage Optimization
- **Lifecycle Policies**: Archive old data to cheaper storage
- **Intelligent Tiering**: Automatic storage class optimization
- **Data Deduplication**: Remove redundant data
- **Compression**: Use efficient file formats

### Redshift Optimization (if enabled)
- **Workload Management**: Query queue configuration
- **Distribution Keys**: Optimize data distribution
- **Sort Keys**: Improve query performance
- **VACUUM**: Regular maintenance operations

## Security Best Practices

### IAM Configuration
- **Least Privilege**: Minimal required permissions
- **Role-Based Access**: Separate roles for different functions
- **Cross-Account Access**: Secure multi-account setup
- **Temporary Credentials**: Use IAM roles instead of keys

### Data Encryption
- **S3 Encryption**: Server-side encryption with KMS
- **Glue Encryption**: Encrypt data in transit and at rest
- **Redshift Encryption**: Database and backup encryption
- **Network Security**: VPC and security group configuration

### Access Logging
- **CloudTrail**: API call logging and monitoring
- **S3 Access Logs**: Bucket access logging
- **VPC Flow Logs**: Network traffic monitoring
- **Application Logs**: Custom application logging

## Testing

### Unit Tests
```bash
# Test Glue job transformations
pytest tests/test_glue_job.py -v

# Test data validation functions
pytest tests/test_validators.py -v
```

### Integration Tests
```bash
# Test complete pipeline with sample data
python tests/integration_test.py --environment dev

# Test infrastructure deployment
terraform plan -var-file=config/test.tfvars
```

### Performance Tests
```bash
# Load test with large dataset
python tests/performance_test.py --size large

# Benchmark query performance
python tests/query_benchmark.py --queries config/test_queries.sql
```

## Deployment Strategies

### Development Environment
- **Single Node**: Cost-effective for development
- **Small Datasets**: Limited data for faster testing
- **Frequent Updates**: Rapid iteration and testing

### Staging Environment
- **Production-like**: Mirror production configuration
- **Full Dataset**: Complete data for integration testing
- **Automated Testing**: CI/CD pipeline integration

### Production Environment
- **High Availability**: Multi-AZ deployment
- **Auto Scaling**: Dynamic resource scaling
- **Monitoring**: Comprehensive monitoring and alerting
- **Backup/Recovery**: Regular backups and disaster recovery

## Troubleshooting

### Common Issues

1. **Glue Job Failures**
   ```bash
   # Check job logs
   aws logs describe-log-groups --log-group-name-prefix /aws-glue/jobs/
   
   # Review job metrics
   aws glue get-job-run --job-name covid-data-etl --run-id jr_xxx
   ```

2. **S3 Access Issues**
   ```bash
   # Check bucket permissions
   aws s3api get-bucket-policy --bucket your-bucket-name
   
   # Test object access
   aws s3 ls s3://your-bucket-name/prefix/
   ```

3. **Schema Evolution Problems**
   ```bash
   # Check Glue catalog
   aws glue get-table --database-name covid_db --name covid_data
   
   # Update schema
   python scripts/update_schema.py --table covid_data
   ```

### Debug Commands

```bash
# View Glue job details
aws glue get-job --job-name covid-data-etl

# List recent job runs
aws glue get-job-runs --job-name covid-data-etl --max-results 10

# Check S3 bucket contents
aws s3 ls s3://your-processed-bucket/year=2024/month=01/ --recursive

# Monitor Redshift queries (if enabled)
aws redshift describe-clusters --cluster-identifier covid-warehouse
```

## Performance Optimization

### Glue Job Tuning
- **Worker Configuration**: Optimize DPU allocation
- **Parallelism**: Configure optimal partition counts
- **Memory Management**: Tune Spark memory settings
- **Caching**: Cache frequently accessed datasets

### Query Optimization
- **Partition Pruning**: Filter by partition keys
- **Columnar Storage**: Use Parquet format benefits
- **Predicate Pushdown**: Apply filters early
- **Join Optimization**: Optimize join strategies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow AWS best practices
4. Add comprehensive tests
5. Update documentation
6. Submit a pull request

## License

This project is licensed under the MIT License.