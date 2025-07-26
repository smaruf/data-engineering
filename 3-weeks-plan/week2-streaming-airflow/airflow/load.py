# airflow/load.py
import json
import logging

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
