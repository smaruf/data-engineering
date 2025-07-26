from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import json
import logging

# Import the plotting function from covid_plotter.py
from airflow.covid_plotter import plot_covid_data

def extract_covid_data(**kwargs):
    url = "https://disease.sh/v3/covid-19/all"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        kwargs['ti'].xcom_push(key='covid_data', value=data)
    except Exception as e:
        logging.error(f"Failed to fetch COVID data: {e}")
        raise

def transform_covid_data(**kwargs):
    ti = kwargs['ti']
    data = ti.xcom_pull(key='covid_data', task_ids='extract_covid_data')
    if not data:
        logging.error("No data received from extract_covid_data")
        raise ValueError("No data to transform")
    transformed = {
        'cases': data.get('cases'),
        'deaths': data.get('deaths'),
        'recovered': data.get('recovered'),
        'updated': data.get('updated')
    }
    ti.xcom_push(key='transformed_covid_data', value=transformed)

def load_covid_data(**kwargs):
    ti = kwargs['ti']
    transformed = ti.xcom_pull(key='transformed_covid_data', task_ids='transform_covid_data')
    if not transformed:
        logging.error("No transformed data for loading")
        raise ValueError("No transformed data")
    try:
        with open('/tmp/covid_summary.json', 'w') as f:
            json.dump(transformed, f)
        print(f"Saved transformed data: {transformed}")
    except Exception as e:
        logging.error(f"Error saving transformed data: {e}")
        raise

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
