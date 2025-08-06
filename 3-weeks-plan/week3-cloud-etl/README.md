# Week 3 – Serverless Data Pipeline on AWS

**Project:** COVID-19 ETL Pipeline with AWS Glue & S3  
**Tech Stack:** AWS S3, AWS Glue, PySpark, Terraform, Redshift (optional)

## 🔹 Description

This project demonstrates a serverless data pipeline on AWS that processes COVID-19 data using cloud-native services. The pipeline extracts raw CSV data from S3, transforms it using AWS Glue with PySpark, and outputs the processed data to a partitioned S3 location for efficient querying.

### Key Features:
- **Serverless Architecture**: No infrastructure management required
- **Scalable Processing**: AWS Glue automatically scales based on data volume
- **Partitioned Storage**: Data organized by year/month for optimal query performance
- **Infrastructure as Code**: Terraform configuration for reproducible deployments
- **Data Quality**: Built-in data validation and cleaning steps

## 🏗️ Architecture

```
Raw CSV Data (S3) 
    ↓
AWS Glue ETL Job (PySpark)
    ↓
Processed Parquet Data (S3 - Partitioned)
    ↓
Optional: Amazon Redshift (Data Warehouse)
```

## 📁 Project Structure

```
week3-cloud-etl/
├── glue_job/
│   └── covid_transform.py      # PySpark ETL script for AWS Glue
├── terraform/
│   └── s3_redshift_setup.tf    # Infrastructure configuration
└── README.md                   # Project documentation
```

### File Descriptions:

- **`glue_job/covid_transform.py`**: Main ETL script containing PySpark code for:
  - Reading raw COVID-19 CSV data from S3
  - Data cleaning and validation
  - Date formatting and standardization
  - Adding calculated fields (year, month, day)
  - Writing partitioned Parquet files to S3

- **`terraform/s3_redshift_setup.tf`**: Terraform configuration for:
  - S3 buckets for raw and processed data
  - IAM roles and policies for Glue jobs
  - Optional Redshift cluster for data warehousing
  - Security configurations and best practices

## 🚀 Deployment Steps

### Prerequisites:
- AWS CLI configured with appropriate credentials
- Terraform installed (version >= 1.0)
- AWS account with permissions for S3, Glue, IAM, and optionally Redshift

### Step 1: Deploy Infrastructure

```bash
cd terraform/

# Initialize Terraform
terraform init

# Plan the deployment
terraform plan

# Apply the infrastructure
terraform apply
```

### Step 2: Upload Sample Data

```bash
# Upload your COVID-19 CSV files to the raw data bucket
aws s3 cp your-covid-data.csv s3://your-raw-bucket-name/input/
```

### Step 3: Create and Run Glue Job

```bash
# Create Glue job using AWS CLI or Console
aws glue create-job \
    --name "covid-etl-job" \
    --role "arn:aws:iam::your-account:role/week3-cloud-etl-glue-job-role-dev" \
    --command '{
        "name": "glueetl",
        "scriptLocation": "s3://your-scripts-bucket/covid_transform.py"
    }'

# Run the job
aws glue start-job-run \
    --job-name "covid-etl-job" \
    --arguments '{
        "--input_s3_path": "s3://your-raw-bucket/input/",
        "--output_s3_path": "s3://your-processed-bucket/output/"
    }'
```

### Step 4: Monitor Job Execution

- Check job status in AWS Glue Console
- View CloudWatch logs for detailed execution information
- Verify output data in the processed data S3 bucket

## 🔧 Configuration Options

### Terraform Variables:

- `aws_region`: AWS region for resource deployment (default: us-east-1)
- `project_name`: Project name for resource tagging (default: week3-cloud-etl)
- `environment`: Environment designation (default: dev)
- `enable_redshift`: Create Redshift cluster (default: false)

### Glue Job Parameters:

- `input_s3_path`: S3 path to raw CSV files
- `output_s3_path`: S3 path for processed Parquet files

## 📊 Data Processing Details

### Input Data Format:
- CSV files with COVID-19 statistics
- Expected columns: date, country, cases, deaths, recovered

### Transformations Applied:
1. **Data Cleaning**: Remove null values in critical columns
2. **Date Standardization**: Convert dates to standard format
3. **Country Normalization**: Clean and standardize country names
4. **Derived Fields**: Add year, month, day columns for partitioning
5. **Data Quality**: Add quality score flags

### Output Data Format:
- Parquet files for efficient storage and querying
- Partitioned by year and month
- Snappy compression for optimal performance

## 🧪 Testing & Validation

### Manual Testing:
1. Upload sample CSV data to input S3 bucket
2. Run Glue job with test parameters
3. Verify output data structure and content
4. Check partition organization in S3

### Data Quality Checks:
- Row count validation (input vs output)
- Data type verification
- Partition integrity checks
- Null value handling verification

## 💡 Best Practices Implemented

- **Security**: IAM roles with least privilege access
- **Cost Optimization**: Use of appropriate instance types and compression
- **Monitoring**: CloudWatch integration for job monitoring
- **Scalability**: Partitioned data for efficient querying
- **Maintainability**: Well-documented code with clear separation of concerns

## 🔗 Related Resources

- [AWS Glue Documentation](https://docs.aws.amazon.com/glue/)
- [PySpark Documentation](https://spark.apache.org/docs/latest/api/python/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest)
- [Amazon S3 Best Practices](https://docs.aws.amazon.com/s3/latest/userguide/best-practices.html)

## 📝 Next Steps

1. Implement data catalog with AWS Glue Crawler
2. Add data lineage tracking
3. Set up automated job scheduling
4. Implement data quality monitoring with AWS Deequ
5. Add integration with Amazon QuickSight for visualization

---

**Author**: Data Engineering Team  
**Date**: 2024  
**Version**: 1.0