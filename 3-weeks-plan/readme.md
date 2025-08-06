# 🧠 Data Engineering Mini Projects

Welcome! This repository contains a series of data engineering projects built over 3 weeks, focusing on batch ETL, real-time streaming, orchestration, and cloud data workflows.

---

## 📅 Week 1 – Batch ETL Pipeline

**Project:** COVID-19 Data ETL Pipeline  
**Tech Stack:** Python, Pandas, PostgreSQL, SQLAlchemy  

### 🔹 Description  
This project extracts COVID-19 statistics from a public API, transforms the data with pandas, and loads it into a PostgreSQL database.  
Airflow DAG added in Week 2 for scheduling.

### 📁 Structure  
week1-batch-etl/  
├── etl_pipeline.py  
├── requirements.txt  
├── config.ini  
└── README.md  

### 🚀 How to Run  
cd week1-batch-etl  
pip install -r requirements.txt  
python etl_pipeline.py  

---

## 📅 Week 2 – Streaming + Orchestration

**Project 1:** Real-Time Market Data Stream (Simulated)  
**Tech Stack:** Python, Apache Kafka  

**Project 2:** Airflow DAG for Batch ETL  
**Tech Stack:** Apache Airflow  

### 🔹 Description  
- Kafka producer generates random market data every second.  
- Kafka consumer reads, parses, and writes to a local DB or file.  
- Airflow DAG schedules the Week 1 batch pipeline with retries and alerts.

### 📁 Structure  
week2-streaming-airflow/  
├── kafka/  
│   ├── producer.py  
│   └── consumer.py  
├── airflow/  
│   └── dags/  
│       └── covid_etl_dag.py  
└── README.md  

### 🚀 How to Run Kafka (local)  
docker-compose up -d  # start Kafka  
python kafka/producer.py  
python kafka/consumer.py  

### 🚀 How to Run Airflow  
cd airflow  
docker-compose up  

---

## 📅 Week 3 – Cloud Data Pipeline (AWS)

**Project:** Serverless Data Pipeline on AWS  
**Tech Stack:** AWS S3, AWS Glue, PySpark, Redshift (optional)

### 🔹 Description  
- Uploads raw CSV data to S3.  
- AWS Glue ETL job cleans and transforms data using PySpark.  
- Outputs to partitioned S3 location or Redshift.

### 📁 Structure  
week3-cloud-etl/  
├── glue_job/  
│   └── covid_transform.py  
├── terraform/  
│   └── s3_redshift_setup.tf  
└── README.md  

### 🚀 How to Deploy  
```bash
cd week3-cloud-etl/terraform
terraform init && terraform apply
```

### 🌐 AWS Setup  
- S3 buckets for raw and processed data  
- AWS Glue job with PySpark transformation  
- IAM roles and policies  
- (Optional) Redshift cluster via Terraform  

---

## 🔗 Useful Links  
- DataTalksClub DE Zoomcamp: https://github.com/DataTalksClub/data-engineering-zoomcamp  
- Airflow Docs: https://airflow.apache.org/docs/  
- Confluent Kafka Python: https://developer.confluent.io/get-started/python/  
- AWS Glue Tutorial: https://docs.aws.amazon.com/glue/latest/dg/start-working.html  

---

## 🧔 About Me  
**Muhammad Shamsul Maruf**  
Backend & Data Engineer | Java, Python, Kafka, AWS  
LinkedIn: https://www.linkedin.com/in/muhammad-shamsul-maruf-79905161/  
GitHub: https://github.com/smaruf  
