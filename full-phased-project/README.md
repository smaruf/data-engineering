# 🚀 Full Phased Data Engineering Project

A comprehensive data engineering project demonstrating end-to-end data pipeline development across three distinct phases: Batch ETL, Streaming & Orchestration, and Cloud Data Pipeline.

## 📋 Project Overview

This project combines multiple data engineering concepts and technologies into a cohesive, production-ready pipeline system. Each phase builds upon the previous one, creating a complete data engineering ecosystem.

### 🎯 Objectives
- Demonstrate batch data processing with ETL pipelines
- Implement real-time streaming data processing
- Build cloud-native serverless data pipelines
- Showcase data orchestration and monitoring
- Provide a complete data engineering learning experience

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Phase 1       │    │   Phase 2       │    │   Phase 3       │
│   Batch ETL     │───▶│   Streaming &   │───▶│   Cloud         │
│                 │    │   Orchestration │    │   Pipeline      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
full-phased-project/
├── phase1-batch-etl/           # Batch ETL Pipeline
│   ├── src/                    # Source code
│   ├── tests/                  # Unit tests
│   └── config/                 # Configuration files
├── phase2-streaming-orchestration/  # Streaming & Orchestration
│   ├── kafka/                  # Kafka producer/consumer
│   ├── airflow/                # Airflow DAGs and plugins
│   ├── src/                    # Source code
│   └── tests/                  # Unit tests
├── phase3-cloud-pipeline/      # Cloud Data Pipeline
│   ├── glue_job/              # AWS Glue ETL jobs
│   ├── terraform/             # Infrastructure as Code
│   ├── lambda/                # Lambda functions
│   ├── src/                   # Source code
│   └── tests/                 # Unit tests
├── shared/                    # Shared utilities and resources
│   ├── utils/                 # Common utilities
│   ├── database/              # Database scripts and schemas
│   └── monitoring/            # Monitoring and logging
├── docs/                      # Project documentation
│   ├── architecture/          # Architecture diagrams and docs
│   ├── api/                   # API documentation
│   └── deployment/            # Deployment guides
├── scripts/                   # Automation scripts
│   ├── setup/                 # Environment setup scripts
│   ├── deployment/            # Deployment scripts
│   └── monitoring/            # Monitoring scripts
├── tests/                     # Integration tests
├── config/                    # Global configuration
├── data/                      # Data storage
│   ├── raw/                   # Raw data files
│   ├── processed/             # Processed data
│   └── output/                # Final output data
├── logs/                      # Application logs
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # Multi-service container setup
├── Makefile                   # Build and deployment automation
└── .env.example              # Environment variables template
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Docker & Docker Compose
- PostgreSQL
- AWS CLI (for Phase 3)
- Terraform (for Phase 3)

### Setup
1. **Clone and navigate to project**
   ```bash
   git clone <repository-url>
   cd full-phased-project
   ```

2. **Install dependencies**
   ```bash
   make install
   # or
   pip install -r requirements.txt
   ```

3. **Setup environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize project**
   ```bash
   make setup
   ```

## 📖 Phase Details

### Phase 1: Batch ETL Pipeline
**Tech Stack:** Python, Pandas, PostgreSQL, SQLAlchemy

- Extract COVID-19 data from public APIs
- Transform data using pandas
- Load into PostgreSQL database
- Data validation and quality checks
- Automated error handling and logging

[📚 Phase 1 Documentation](phase1-batch-etl/README.md)

### Phase 2: Streaming & Orchestration
**Tech Stack:** Apache Kafka, Apache Airflow, Python

- Real-time market data streaming with Kafka
- Airflow DAGs for pipeline orchestration
- Data processing and transformation
- Monitoring and alerting
- Retry mechanisms and error handling

[📚 Phase 2 Documentation](phase2-streaming-orchestration/README.md)

### Phase 3: Cloud Data Pipeline
**Tech Stack:** AWS S3, AWS Glue, PySpark, Terraform, Redshift

- Serverless ETL with AWS Glue
- Infrastructure as Code with Terraform
- Scalable data processing with PySpark
- Data warehousing with Redshift
- Cloud-native monitoring and logging

[📚 Phase 3 Documentation](phase3-cloud-pipeline/README.md)

## 🛠️ Development

### Running Individual Phases
```bash
# Phase 1: Batch ETL
make run-phase1

# Phase 2: Streaming & Orchestration
make run-phase2

# Phase 3: Cloud Pipeline
make run-phase3
```

### Running All Phases
```bash
make run-all
```

### Testing
```bash
# Run all tests
make test

# Run specific phase tests
make test-phase1
make test-phase2
make test-phase3
```

## 📊 Monitoring & Observability

- **Logging:** Centralized logging with structured logs
- **Metrics:** Custom metrics for pipeline performance
- **Alerting:** Automated alerts for failures and anomalies
- **Dashboards:** Real-time monitoring dashboards

## 🚀 Deployment

### Local Development
```bash
docker-compose up -d
```

### Production Deployment
```bash
# Deploy infrastructure
make deploy-infrastructure

# Deploy applications
make deploy-applications
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For questions and support:
- Create an issue in the repository
- Contact: Muhammad Shamsul Maruf
- LinkedIn: [muhammad-shamsul-maruf](https://www.linkedin.com/in/muhammad-shamsul-maruf-79905161/)

---

**Built with ❤️ for the Data Engineering Community**