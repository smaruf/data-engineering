from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Import extraction and loading functions from airflow/ directory
from airflow.extract import extract_covid_data
from airflow.load import load_covid_data
from airflow.transform import transform_covid_data
from airflow.covid_plotter import plot_covid_data

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='covid_etl_dag',
    default_args=default_args,
    description='ETL pipeline for COVID-19 data',
    schedule_interval='@daily',
    catchup=False,
) as dag:

    extract = PythonOperator(
        task_id='extract_covid_data',
        python_callable=extract_covid_data,
        provide_context=True,
    )

    transform = PythonOperator(
        task_id='transform_covid_data',
        python_callable=transform_covid_data,
        provide_context=True,
    )

    load = PythonOperator(
        task_id='load_covid_data',
        python_callable=load_covid_data,
        provide_context=True,
    )

    plot = PythonOperator(
        task_id='plot_covid_data',
        python_callable=plot_covid_data,
        provide_context=False,
    )

    extract >> transform >> load >> plot
