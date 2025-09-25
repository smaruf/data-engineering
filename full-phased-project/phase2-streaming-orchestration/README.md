# Phase 2: Streaming & Orchestration

## Overview

This phase implements real-time data streaming with Apache Kafka and workflow orchestration with Apache Airflow. It builds upon Phase 1 by adding streaming capabilities and automated scheduling for batch ETL processes.

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Kafka     │    │  Airflow    │    │   Phase 1   │
│ Streaming   │────┤Orchestration│────┤ Batch ETL   │
│             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Features

### Kafka Streaming
- **Real-time Data Ingestion**: Continuous data streaming from multiple sources
- **Multi-source Integration**: Financial markets, cryptocurrency, forex data
- **Message Processing**: Scalable consumer groups with parallel processing
- **Data Persistence**: Configurable data storage and retention
- **Error Handling**: Dead letter queues and retry mechanisms

### Airflow Orchestration
- **DAG Management**: Complex workflow scheduling and monitoring
- **Task Dependencies**: Define complex data pipeline dependencies
- **Retry Logic**: Automatic retry with exponential backoff
- **Alerting**: Email and Slack notifications for failures
- **Monitoring**: Web UI for pipeline monitoring and debugging

## Tech Stack

- **Apache Kafka**: Distributed streaming platform
- **Apache Airflow**: Workflow orchestration engine
- **Python**: Core programming language
- **Docker**: Containerization and service orchestration
- **PostgreSQL**: Metadata storage for Airflow
- **Redis**: Message broker for Airflow Celery executor

## Project Structure

```
phase2-streaming-orchestration/
├── kafka/
│   ├── __init__.py
│   ├── producer.py              # Market data producer
│   ├── consumer.py              # Market data consumer
│   ├── config.py                # Kafka configuration
│   └── utils/
│       ├── __init__.py
│       ├── serializers.py       # Custom serializers
│       └── monitoring.py        # Kafka monitoring
├── airflow/
│   ├── dags/
│   │   ├── covid_etl_dag.py     # COVID-19 ETL scheduling
│   │   ├── market_data_dag.py   # Market data processing
│   │   └── data_quality_dag.py  # Data quality checks
│   ├── plugins/
│   │   ├── __init__.py
│   │   └── custom_operators/    # Custom Airflow operators
│   ├── config/
│   │   └── airflow.cfg          # Airflow configuration
│   └── Dockerfile               # Airflow container setup
├── src/
│   ├── __init__.py
│   ├── streaming/
│   │   ├── __init__.py
│   │   ├── processors.py        # Stream processing logic
│   │   └── connectors.py        # External system connectors
│   └── orchestration/
│       ├── __init__.py
│       ├── tasks.py             # Custom Airflow tasks
│       └── sensors.py           # Custom sensors
├── tests/
│   ├── __init__.py
│   ├── test_kafka.py           # Kafka integration tests
│   └── test_airflow.py         # Airflow DAG tests
├── config/
│   ├── kafka.properties        # Kafka configuration
│   └── logging.conf            # Logging configuration
├── docker-compose.kafka.yml    # Kafka stack
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Quick Start

### Prerequisites

1. Docker and Docker Compose
2. Python 3.8+
3. Apache Kafka (or use Docker setup)
4. Apache Airflow

### Installation

1. **Start Kafka Stack**:
   ```bash
   cd phase2-streaming-orchestration
   docker-compose -f docker-compose.kafka.yml up -d
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize Airflow**:
   ```bash
   export AIRFLOW_HOME=$(pwd)/airflow
   airflow db init
   airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
   ```

4. **Start Airflow Services**:
   ```bash
   airflow scheduler &
   airflow webserver --port 8081
   ```

### Running Kafka Streaming

1. **Start Producer**:
   ```bash
   python kafka/producer.py
   ```

2. **Start Consumer**:
   ```bash
   python kafka/consumer.py
   ```

3. **Monitor Kafka**:
   - Kafka UI: http://localhost:8080
   - View topics, partitions, and messages

### Running Airflow

1. **Access Web UI**: http://localhost:8081
2. **Enable DAGs**: Toggle DAGs in the web interface
3. **Monitor Execution**: View task logs and execution history

## Configuration

### Kafka Configuration (`config/kafka.properties`)

```properties
bootstrap.servers=localhost:9092
key.serializer=org.apache.kafka.common.serialization.StringSerializer
value.serializer=org.apache.kafka.common.serialization.JsonSerializer
auto.offset.reset=earliest
group.id=market-data-consumers
```

### Airflow Configuration

Environment variables in `.env`:
```bash
AIRFLOW__CORE__EXECUTOR=CeleryExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql://airflow:airflow@localhost/airflow
AIRFLOW__CELERY__BROKER_URL=redis://localhost:6379/0
```

## Data Sources

### Streaming Data Sources
1. **Binance API**: Cryptocurrency prices (BTC/USDT)
2. **Coinbase API**: Cryptocurrency prices (ETH/USD)
3. **Exchange Rate API**: Forex rates (EUR/USD)
4. **Custom Sources**: Simulated market data

### Batch Data Sources
- COVID-19 APIs (from Phase 1)
- Financial market data APIs
- Custom data feeds

## Kafka Topics

- `market-data`: Real-time market price updates
- `covid-updates`: COVID-19 data updates
- `data-quality-alerts`: Data quality monitoring alerts
- `system-metrics`: Application performance metrics

## Airflow DAGs

### 1. COVID ETL DAG (`covid_etl_dag.py`)
- **Schedule**: Daily at 6 AM UTC
- **Tasks**: Extract → Transform → Load → Validate
- **Retries**: 3 attempts with 5-minute intervals
- **Alerts**: Email on failure

### 2. Market Data DAG (`market_data_dag.py`)
- **Schedule**: Every 15 minutes
- **Tasks**: Process streaming data → Aggregate → Store
- **Dependencies**: Market hours detection
- **Monitoring**: Data freshness checks

### 3. Data Quality DAG (`data_quality_dag.py`)
- **Schedule**: Hourly
- **Tasks**: Validate data quality → Generate reports → Alert on issues
- **Metrics**: Completeness, accuracy, timeliness

## Monitoring & Alerting

### Kafka Monitoring
- **Metrics**: Throughput, latency, consumer lag
- **Tools**: Kafka UI, JMX metrics
- **Alerts**: Consumer lag, partition failures

### Airflow Monitoring
- **Web UI**: Real-time DAG and task monitoring
- **Metrics**: Task success rates, execution times
- **Alerts**: Email, Slack, PagerDuty integration

### System Health
- **Application Logs**: Structured logging with ELK stack
- **Performance Metrics**: CPU, memory, disk usage
- **Alerting**: Threshold-based alerts

## Data Processing Patterns

### Stream Processing
- **Windowed Aggregations**: Time-based data aggregation
- **Event Deduplication**: Handle duplicate messages
- **Schema Evolution**: Support for schema changes
- **State Management**: Stateful stream processing

### Batch Processing
- **Incremental Processing**: Process only new/changed data
- **Backfill Support**: Reprocess historical data
- **Partition Management**: Efficient data partitioning
- **Data Lineage**: Track data flow and transformations

## Error Handling

### Kafka Error Handling
- **Dead Letter Queues**: Handle poison messages
- **Retry Policies**: Configurable retry attempts
- **Circuit Breakers**: Prevent cascade failures
- **Message Validation**: Schema validation

### Airflow Error Handling
- **Task Retries**: Automatic retry with backoff
- **Failure Callbacks**: Custom failure handling
- **SLA Monitoring**: Service level agreement tracking
- **Alerting**: Multi-channel alert delivery

## Testing

### Unit Tests
```bash
pytest tests/test_kafka.py -v
pytest tests/test_airflow.py -v
```

### Integration Tests
```bash
pytest tests/integration/ -v
```

### DAG Tests
```bash
# Test DAG loading
airflow dags list

# Test task execution
airflow tasks test covid_etl_dag extract_data 2024-01-01
```

## Performance Optimization

### Kafka Optimization
- **Partition Strategy**: Optimal partition count and key distribution
- **Batch Processing**: Batch size and linger time optimization
- **Compression**: Message compression (snappy, lz4, gzip)
- **Connection Pooling**: Reuse connections for better performance

### Airflow Optimization
- **Parallelism**: Configure task and DAG parallelism
- **Resource Management**: CPU and memory allocation
- **Database Optimization**: PostgreSQL tuning for metadata
- **Caching**: Result caching for expensive operations

## Deployment

### Development Environment
```bash
make dev-setup
```

### Production Deployment
```bash
# Deploy with Kubernetes
kubectl apply -f k8s/

# Or with Docker Swarm
docker stack deploy -c docker-stack.yml data-eng-phase2
```

## Troubleshooting

### Common Issues

1. **Kafka Connection Errors**
   - Check broker availability
   - Verify network connectivity
   - Review security configurations

2. **Airflow Task Failures**
   - Check task logs in web UI
   - Verify database connections
   - Review resource constraints

3. **Consumer Lag**
   - Monitor consumer group status
   - Scale consumer instances
   - Optimize processing logic

### Debug Commands

```bash
# Kafka topic information
kafka-topics --bootstrap-server localhost:9092 --describe --topic market-data

# Consumer group status
kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group market-data-consumers

# Airflow task logs
airflow tasks logs covid_etl_dag extract_data 2024-01-01 1
```

## Security

### Kafka Security
- **SASL Authentication**: Username/password authentication
- **SSL Encryption**: TLS encryption for data in transit
- **ACL Authorization**: Topic-level access control
- **Network Security**: VPC and firewall configurations

### Airflow Security
- **RBAC**: Role-based access control
- **Connection Encryption**: Encrypted connections to external systems
- **Secrets Management**: Secure storage of credentials
- **Audit Logging**: Track user actions and system changes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Follow code style guidelines
5. Submit a pull request

## License

This project is licensed under the MIT License.