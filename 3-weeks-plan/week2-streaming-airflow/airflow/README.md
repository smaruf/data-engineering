# Airflow Streaming – Week 2

This directory contains resources and scripts for setting up and running Apache Airflow workflows focused on streaming data pipelines as part of the 3-weeks data engineering plan.

## Contents

- DAGs for streaming data processing
- Airflow configuration files
- Helper scripts for pipeline orchestration

## Getting Started

1. **Install Airflow**  
   Follow [Airflow installation guide](https://airflow.apache.org/docs/apache-airflow/stable/installation/index.html).

2. **Set up environment**  
   Configure your `airflow.cfg` and environment variables as needed.

3. **Initialize Airflow**  
   Run `airflow db init` to set up the metadata database.

4. **Start Airflow services**  
   Launch scheduler and webserver using:
   ```
   airflow scheduler
   airflow webserver
   ```

5. **Add DAGs**  
   Place custom DAG scripts in the `dags/` folder.

## Usage

Monitor and trigger streaming workflows from the Airflow UI. Check logs and task statuses for debugging.

## Contributing

Pull requests welcome. Please follow best coding practices.

## License

MIT
