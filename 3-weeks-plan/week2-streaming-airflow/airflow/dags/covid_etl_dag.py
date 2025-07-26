from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import json

def extract_covid_data(**kwargs):
    url = "https://disease.sh/v3/covid-19/all"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Push to XCom for downstream tasks
        kwargs['ti'].xcom_push(key='covid_data', value=data)
    else:
        raise Exception("Failed to fetch COVID data")

def transform_covid_data(**kwargs):
    ti = kwargs['ti']
    data = ti.xcom_pull(key='covid_data', task_ids='extract_covid_data')
    # Example transformation: select only total cases, deaths, recovered
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
    # Example: save to file (you can adapt to save to DB, etc.)
    with open('/tmp/covid_summary.json', 'w') as f:
        json.dump(transformed, f)
    print(f"Saved transformed data: {transformed}")

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

    extract >> transform >> load
