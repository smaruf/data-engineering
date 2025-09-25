"""
COVID-19 ETL DAG for Airflow
Orchestrates the COVID-19 data pipeline from Phase 1 with enhanced monitoring and error handling
"""

from datetime import datetime, timedelta
import os
import sys
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.email_operator import EmailOperator
from airflow.sensors.filesystem import FileSensor
from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import Variable
from airflow.utils.dates import days_ago

# Add project paths
sys.path.append('/opt/airflow/dags')
sys.path.append('/app/full-phased-project')

# Default arguments for the DAG
default_args = {
    'owner': 'data-engineering-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
}

# DAG definition
dag = DAG(
    'covid_etl_pipeline',
    default_args=default_args,
    description='COVID-19 Data ETL Pipeline with enhanced monitoring',
    schedule_interval='0 6 * * *',  # Daily at 6 AM UTC
    max_active_runs=1,
    catchup=False,
    tags=['covid', 'etl', 'batch', 'healthcare'],
)


def check_data_freshness(**context):
    """Check if the source data is fresh enough to process"""
    import requests
    from datetime import datetime, timezone
    
    try:
        # Check disease.sh API availability and data freshness
        response = requests.get('https://disease.sh/v3/covid-19/all', timeout=30)
        response.raise_for_status()
        
        data = response.json()
        updated_timestamp = data.get('updated', 0)
        
        if updated_timestamp:
            updated_date = datetime.fromtimestamp(updated_timestamp / 1000, tz=timezone.utc)
            hours_since_update = (datetime.now(timezone.utc) - updated_date).total_seconds() / 3600
            
            if hours_since_update > 48:  # Data older than 48 hours
                raise ValueError(f"Data is {hours_since_update:.1f} hours old, too stale to process")
        
        print(f"Data freshness check passed. Data updated: {updated_date}")
        return True
        
    except Exception as e:
        print(f"Data freshness check failed: {str(e)}")
        raise


def extract_covid_data(**context):
    """Extract COVID-19 data using the Phase 1 extractor"""
    import sys
    import os
    
    # Add Phase 1 path
    phase1_path = '/app/full-phased-project/phase1-batch-etl/src'
    sys.path.insert(0, phase1_path)
    
    from extractors.covid_api import CovidAPIExtractor
    
    try:
        # Initialize extractor
        config_path = os.path.join(phase1_path, '..', 'config', 'config.ini')
        extractor = CovidAPIExtractor(config_path)
        
        # Extract data
        raw_data = extractor.extract_disease_sh_data()
        
        if not raw_data:
            raise ValueError("No data extracted from COVID API")
        
        print(f"Extracted {len(raw_data)} records from COVID API")
        
        # Store data in XCom for next task
        context['task_instance'].xcom_push(key='raw_data', value=raw_data)
        
        return len(raw_data)
        
    except Exception as e:
        print(f"Data extraction failed: {str(e)}")
        raise


def validate_raw_data(**context):
    """Validate the extracted raw data"""
    raw_data = context['task_instance'].xcom_pull(key='raw_data', task_ids='extract_data')
    
    if not raw_data:
        raise ValueError("No raw data received from extraction task")
    
    # Basic validation checks
    validation_errors = []
    
    for i, record in enumerate(raw_data):
        # Check required fields
        required_fields = ['country', 'confirmed', 'deaths', 'recovered']
        for field in required_fields:
            if field not in record or record[field] is None:
                validation_errors.append(f"Record {i}: Missing field '{field}'")
        
        # Check data types and ranges
        if 'confirmed' in record and (not isinstance(record['confirmed'], (int, float)) or record['confirmed'] < 0):
            validation_errors.append(f"Record {i}: Invalid confirmed cases value")
        
        if 'deaths' in record and (not isinstance(record['deaths'], (int, float)) or record['deaths'] < 0):
            validation_errors.append(f"Record {i}: Invalid deaths value")
    
    # Fail if too many validation errors
    if len(validation_errors) > len(raw_data) * 0.1:  # More than 10% error rate
        raise ValueError(f"Too many validation errors: {len(validation_errors)}")
    
    if validation_errors:
        print(f"Validation warnings: {validation_errors[:10]}")  # Show first 10 errors
    
    print(f"Data validation completed. {len(raw_data)} records validated with {len(validation_errors)} warnings")
    return len(validation_errors)


def transform_covid_data(**context):
    """Transform the extracted COVID-19 data"""
    import sys
    import os
    
    # Add Phase 1 path
    phase1_path = '/app/full-phased-project/phase1-batch-etl/src'
    sys.path.insert(0, phase1_path)
    
    from transformers.covid_transformer import CovidTransformer
    
    try:
        # Get raw data from previous task
        raw_data = context['task_instance'].xcom_pull(key='raw_data', task_ids='extract_data')
        
        if not raw_data:
            raise ValueError("No raw data received for transformation")
        
        # Initialize transformer
        config_path = os.path.join(phase1_path, '..', 'config', 'config.ini')
        transformer = CovidTransformer(config_path)
        
        # Transform data
        transformed_data = transformer.transform(raw_data)
        
        if not transformed_data:
            raise ValueError("No data produced by transformation")
        
        print(f"Transformed {len(transformed_data)} records")
        
        # Store transformed data in XCom
        context['task_instance'].xcom_push(key='transformed_data', value=transformed_data)
        
        return len(transformed_data)
        
    except Exception as e:
        print(f"Data transformation failed: {str(e)}")
        raise


def load_covid_data(**context):
    """Load the transformed data into the database"""
    import sys
    import os
    
    # Add Phase 1 path
    phase1_path = '/app/full-phased-project/phase1-batch-etl/src'
    sys.path.insert(0, phase1_path)
    
    from loaders.postgres_loader import PostgresLoader
    
    try:
        # Get transformed data from previous task
        transformed_data = context['task_instance'].xcom_pull(key='transformed_data', task_ids='transform_data')
        
        if not transformed_data:
            raise ValueError("No transformed data received for loading")
        
        # Initialize loader
        config_path = os.path.join(phase1_path, '..', 'config', 'config.ini')
        loader = PostgresLoader(config_path)
        
        # Create tables if they don't exist
        loader.create_tables()
        
        # Load data
        success = loader.load_data(transformed_data)
        
        if not success:
            raise ValueError("Data loading failed")
        
        print(f"Successfully loaded {len(transformed_data)} records to database")
        
        return len(transformed_data)
        
    except Exception as e:
        print(f"Data loading failed: {str(e)}")
        raise


def data_quality_check(**context):
    """Perform data quality checks on the loaded data"""
    
    try:
        # Get PostgreSQL connection
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # Check 1: Record count
        count_query = "SELECT COUNT(*) FROM covid_stats WHERE DATE(processed_at) = CURRENT_DATE"
        record_count = postgres_hook.get_first(count_query)[0]
        
        if record_count == 0:
            raise ValueError("No records found for today's ETL run")
        
        # Check 2: Data completeness
        completeness_query = """
            SELECT 
                COUNT(*) as total_records,
                COUNT(country) as countries_with_names,
                COUNT(confirmed) as records_with_confirmed,
                COUNT(deaths) as records_with_deaths
            FROM covid_stats 
            WHERE DATE(processed_at) = CURRENT_DATE
        """
        
        completeness = postgres_hook.get_first(completeness_query)
        total, countries, confirmed, deaths = completeness
        
        completeness_rate = min(countries, confirmed, deaths) / total * 100
        
        if completeness_rate < 95:  # Less than 95% completeness
            raise ValueError(f"Data completeness too low: {completeness_rate:.1f}%")
        
        # Check 3: Data consistency
        consistency_query = """
            SELECT COUNT(*) 
            FROM covid_stats 
            WHERE DATE(processed_at) = CURRENT_DATE 
            AND (deaths > confirmed OR recovered > confirmed)
        """
        
        inconsistent_records = postgres_hook.get_first(consistency_query)[0]
        
        if inconsistent_records > total * 0.05:  # More than 5% inconsistent
            raise ValueError(f"Too many inconsistent records: {inconsistent_records}")
        
        print(f"Data quality check passed: {record_count} records, {completeness_rate:.1f}% complete, {inconsistent_records} inconsistent")
        
        # Store quality metrics in XCom
        quality_metrics = {
            'record_count': record_count,
            'completeness_rate': completeness_rate,
            'inconsistent_records': inconsistent_records,
            'check_time': datetime.now().isoformat()
        }
        
        context['task_instance'].xcom_push(key='quality_metrics', value=quality_metrics)
        
        return quality_metrics
        
    except Exception as e:
        print(f"Data quality check failed: {str(e)}")
        raise


def generate_summary_report(**context):
    """Generate a summary report of the ETL run"""
    
    try:
        # Get metrics from previous tasks
        extract_count = context['task_instance'].xcom_pull(task_ids='extract_data')
        transform_count = context['task_instance'].xcom_pull(task_ids='transform_data')
        load_count = context['task_instance'].xcom_pull(task_ids='load_data')
        quality_metrics = context['task_instance'].xcom_pull(key='quality_metrics', task_ids='quality_check')
        
        # Generate report
        report = {
            'dag_id': context['dag'].dag_id,
            'run_id': context['run_id'],
            'execution_date': context['execution_date'].isoformat(),
            'start_date': context['dag_run'].start_date.isoformat(),
            'end_date': datetime.now().isoformat(),
            'metrics': {
                'extracted_records': extract_count,
                'transformed_records': transform_count,
                'loaded_records': load_count,
                'data_quality': quality_metrics
            },
            'success': True
        }
        
        # Store report
        context['task_instance'].xcom_push(key='summary_report', value=report)
        
        print(f"ETL Summary Report:")
        print(f"- Extracted: {extract_count} records")
        print(f"- Transformed: {transform_count} records") 
        print(f"- Loaded: {load_count} records")
        print(f"- Quality Score: {quality_metrics.get('completeness_rate', 0):.1f}%")
        
        return report
        
    except Exception as e:
        print(f"Report generation failed: {str(e)}")
        raise


# Task definitions
check_freshness_task = PythonOperator(
    task_id='check_data_freshness',
    python_callable=check_data_freshness,
    dag=dag,
)

extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_covid_data,
    dag=dag,
)

validate_task = PythonOperator(
    task_id='validate_raw_data',
    python_callable=validate_raw_data,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_covid_data,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_data',
    python_callable=load_covid_data,
    dag=dag,
)

quality_check_task = PythonOperator(
    task_id='quality_check',
    python_callable=data_quality_check,
    dag=dag,
)

summary_task = PythonOperator(
    task_id='generate_summary',
    python_callable=generate_summary_report,
    dag=dag,
)

# Notification task (runs on failure)
def send_failure_notification(**context):
    """Send notification on DAG failure"""
    return f"""
    COVID ETL Pipeline Failed
    
    DAG: {context['dag'].dag_id}
    Run ID: {context['run_id']}
    Failed Task: {context.get('task_instance').task_id}
    Execution Date: {context['execution_date']}
    
    Please check the Airflow UI for more details.
    """

failure_notification = EmailOperator(
    task_id='failure_notification',
    to=['data-team@company.com'],
    subject='COVID ETL Pipeline Failed',
    html_content=send_failure_notification,
    dag=dag,
    trigger_rule='one_failed'
)

# Task dependencies
check_freshness_task >> extract_task >> validate_task >> transform_task >> load_task >> quality_check_task >> summary_task
[extract_task, validate_task, transform_task, load_task, quality_check_task] >> failure_notification