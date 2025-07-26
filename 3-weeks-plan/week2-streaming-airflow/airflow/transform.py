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
