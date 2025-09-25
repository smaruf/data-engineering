# Phase 1: Batch ETL Pipeline

## Overview

This phase implements a robust batch ETL (Extract, Transform, Load) pipeline that processes COVID-19 data from public APIs. The pipeline demonstrates core data engineering principles including data extraction, transformation, validation, and loading into a PostgreSQL database.

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Extract   │───▶│  Transform  │───▶│    Load     │
│ (API Data)  │    │  (Pandas)   │    │(PostgreSQL) │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Features

- **Data Extraction**: Fetch COVID-19 statistics from multiple public APIs
- **Data Transformation**: Clean, validate, and standardize data using pandas
- **Data Loading**: Store processed data in PostgreSQL with proper schema
- **Error Handling**: Comprehensive error handling and retry mechanisms
- **Data Validation**: Quality checks and data validation rules
- **Logging**: Structured logging for monitoring and debugging
- **Configuration**: Environment-based configuration management

## Tech Stack

- **Python 3.8+**: Core programming language
- **Pandas**: Data manipulation and analysis
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Primary database
- **Requests**: HTTP library for API calls
- **ConfigParser**: Configuration management

## Project Structure

```
phase1-batch-etl/
├── src/
│   ├── __init__.py
│   ├── etl_pipeline.py      # Main ETL pipeline
│   ├── extractors/          # Data extraction modules
│   │   ├── __init__.py
│   │   ├── covid_api.py     # COVID-19 API extractor
│   │   └── base_extractor.py
│   ├── transformers/        # Data transformation modules
│   │   ├── __init__.py
│   │   ├── covid_transformer.py
│   │   └── base_transformer.py
│   ├── loaders/            # Data loading modules
│   │   ├── __init__.py
│   │   ├── postgres_loader.py
│   │   └── base_loader.py
│   └── utils/              # Utility modules
│       ├── __init__.py
│       ├── database.py
│       ├── validators.py
│       └── logger.py
├── tests/                  # Unit tests
│   ├── __init__.py
│   ├── test_extractors.py
│   ├── test_transformers.py
│   └── test_loaders.py
├── config/                 # Configuration files
│   ├── config.ini
│   └── database_schema.sql
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Quick Start

### Prerequisites

1. Python 3.8 or higher
2. PostgreSQL database
3. Required Python packages (see requirements.txt)

### Installation

1. **Install dependencies**:
   ```bash
   cd phase1-batch-etl
   pip install -r requirements.txt
   ```

2. **Database setup**:
   ```bash
   # Create database
   createdb data_engineering
   
   # Run schema setup
   psql -d data_engineering -f config/database_schema.sql
   ```

3. **Configuration**:
   ```bash
   # Copy and edit configuration
   cp config/config.ini.example config/config.ini
   # Edit config.ini with your database credentials
   ```

### Running the Pipeline

```bash
# Run the complete ETL pipeline
python src/etl_pipeline.py

# Run with specific configuration
python src/etl_pipeline.py --config config/production.ini

# Run in verbose mode
python src/etl_pipeline.py --verbose
```

## Configuration

Edit `config/config.ini` with your settings:

```ini
[postgresql]
host = localhost
port = 5432
database = data_engineering
username = data_eng
password = your_password

[api]
covid_api_url = https://disease.sh/v3/covid-19
rate_limit = 10
timeout = 30
retries = 3

[logging]
level = INFO
format = json
file = logs/etl_pipeline.log
```

## Database Schema

The pipeline creates the following tables:

### covid_stats
- `id` (SERIAL PRIMARY KEY)
- `country` (VARCHAR(100))
- `confirmed` (INTEGER)
- `deaths` (INTEGER)
- `recovered` (INTEGER)
- `active` (INTEGER)
- `date` (TIMESTAMP)
- `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

## Data Sources

1. **Disease.sh API**: COVID-19 statistics by country
2. **Johns Hopkins CSSE**: Historical COVID-19 data
3. **WHO API**: World Health Organization data

## Data Quality Checks

The pipeline includes several data quality checks:

- **Completeness**: Ensure required fields are present
- **Validity**: Check data types and value ranges
- **Consistency**: Verify data consistency across sources
- **Freshness**: Check data recency
- **Accuracy**: Cross-validate with multiple sources

## Error Handling

- **API Failures**: Retry mechanisms with exponential backoff
- **Database Errors**: Transaction rollback and error logging
- **Data Quality Issues**: Skip invalid records with logging
- **Network Issues**: Timeout handling and retries

## Monitoring

The pipeline provides comprehensive monitoring:

- **Execution Metrics**: Runtime, record counts, success rates
- **Data Quality Metrics**: Validation pass/fail rates
- **System Metrics**: Memory usage, CPU utilization
- **Business Metrics**: Data freshness, completeness scores

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test module
pytest tests/test_extractors.py -v
```

## Performance Optimization

- **Batch Processing**: Process data in configurable batch sizes
- **Connection Pooling**: Reuse database connections
- **Parallel Processing**: Multi-threaded data extraction
- **Caching**: Cache API responses to reduce requests
- **Indexing**: Proper database indexes for query performance

## Deployment

### Local Development
```bash
make setup
make run-phase1
```

### Production Deployment
```bash
# Using Docker
docker build -t phase1-batch-etl .
docker run -e DATABASE_URL=$DATABASE_URL phase1-batch-etl

# Using systemd service
sudo systemctl start phase1-etl.service
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check database credentials in config.ini
   - Ensure PostgreSQL is running
   - Verify network connectivity

2. **API Rate Limiting**
   - Adjust rate_limit in configuration
   - Implement exponential backoff
   - Use multiple API keys if available

3. **Memory Issues**
   - Reduce batch_size in configuration
   - Use data streaming for large datasets
   - Monitor memory usage

### Logs

Check logs in:
- `logs/etl_pipeline.log`: Application logs
- `logs/data_quality.log`: Data quality issues
- `logs/performance.log`: Performance metrics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License.