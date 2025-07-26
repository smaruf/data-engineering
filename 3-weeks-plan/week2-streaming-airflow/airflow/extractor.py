# airflow/extract.py
import requests
import logging

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
