from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Import extraction and loading functions from airflow/ directory
from airflow.extract import extract_covid_data
from airflow.load import load_covid_data

# Keep transformation logic here
def transform_covid_data(**kwargs):
    ti = kwargs['ti']
    data = ti.xcom_pull(key='covid_data', task_ids='extract_covid_data')
    if not data:
        raise ValueError("No data to transform")
    transformed = {
        'cases': data.get('cases'),
        'deaths': data.get('deaths'),
        'recovered': data.get('recovered'),
        'updated': data.get('updated')
    }
    ti.xcom_push(key='transformed_covid_data', value=transformed)

# Import the plotting function as before
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
