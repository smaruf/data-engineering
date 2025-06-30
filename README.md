# Data Engineering Learning Journey

Project for learning data engineering as a professional

## 3-Month Data Engineering Learning Plan

### Month 1 — Python Data Engineering + SQL + ETL Basics

#### Learn:
**Python libraries for data engineering:**
- `pandas` (for data manipulation)
- `SQLAlchemy` (Python SQL toolkit)

**SQL deep dive:**
- Complex queries, window functions, joins
- Performance tuning

**ETL concepts:**
- Building simple pipelines

#### Practice:
- Build ETL scripts extracting data from CSV/JSON APIs
- Transform data with pandas
- Load data into a local Postgres DB
- Learn and write complex SQL queries to prepare data sets

#### Resources:
- [Python for Data Analysis by Wes McKinney](https://wesmckinney.com/book/) (focus on pandas)
- [Mode Analytics SQL Tutorial](https://mode.com/sql-tutorial/)
- Intro to ETL with Python and SQL (many tutorials on YouTube)

---

### Month 2 — Apache Spark + Data Pipeline Orchestration (Airflow)

#### Learn:
- Apache Spark fundamentals (PySpark preferred)
- Build batch data processing jobs
- Apache Airflow basics: DAGs, operators, scheduling
- Set up Airflow locally or in Docker

#### Practice:
- Build a Spark job to process a medium-size public dataset (e.g., NYC Taxi Trips, Kaggle datasets)
- Build an Airflow DAG to run your Spark job on schedule and track success/failure

#### Resources:
- [Databricks free courses on Apache Spark](https://databricks.com/learn/spark)
- [Airflow official tutorial](https://airflow.apache.org/docs/apache-airflow/stable/tutorial.html)
- Hands-on projects from GitHub repos for Spark + Airflow integration

---

### Month 3 — Cloud Data Engineering + Streaming (AWS + Kafka)

#### Learn:
- AWS Glue (serverless ETL)
- AWS Redshift (data warehouse)
- AWS Kinesis basics or Apache Kafka (more open source)
- Build real-time data ingestion and processing pipelines

#### Practice:
- Create an ETL job in AWS Glue that extracts from S3 and loads into Redshift
- Build a Kafka producer and consumer app in Python or Java
- Set up a simple streaming pipeline to process data in real-time (Kafka → Spark Streaming or Kinesis Data Analytics)

#### Resources:
- [AWS Glue tutorial](https://aws.amazon.com/glue/getting-started/)
- [Confluent Kafka tutorials](https://developer.confluent.io/learn-kafka/)
- Kafka + Spark Streaming sample projects on GitHub

---

## Bonus Tips

- Document your projects on GitHub with READMEs and architecture diagrams
- Share progress as blog posts or short videos — great for portfolio & networking
- Join data engineering communities (LinkedIn, Reddit r/dataengineering, Slack groups)

---

## Project Structure

This repository will be organized to support the 3-month learning plan:

```
├── month-1-python-sql-etl/
│   ├── pandas-exercises/
│   ├── sql-practice/
│   └── etl-projects/
├── month-2-spark-airflow/
│   ├── spark-jobs/
│   └── airflow-dags/
├── month-3-cloud-streaming/
│   ├── aws-projects/
│   └── kafka-streaming/
└── resources/
    ├── datasets/
    └── documentation/
```
