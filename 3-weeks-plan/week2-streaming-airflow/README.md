### 📅 Week 2 – Streaming + Orchestration
 - Project 1: Real-Time Market Data Stream (Simulated)
   - Tech Stack: Python, Apache Kafka
 - Project 2: Airflow DAG for Batch ETL
   - Tech Stack: Apache Airflow

### 🔹 Description
- Kafka producer generates random market data every second.
- Kafka consumer reads, parses, and writes to a local DB or file.
- Airflow DAG schedules the Week 1 batch pipeline with retries and alerts.
```
📁 Structure
week2-streaming-airflow/
├── kafka/
│ ├── producer.py
│ └── consumer.py
├── airflow/
│ └── dags/
│ └── covid_etl_dag.py
└── README.md
```

### 🚀 How to Run Kafka (local)
```
docker-compose up -d # start Kafka
python kafka/producer.py
python kafka/consumer.py
```
### 🚀 How to Run Airflow
```
cd airflow
docker-compose up
```
