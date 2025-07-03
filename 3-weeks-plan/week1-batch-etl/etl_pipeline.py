import requests
import pandas as pd
from sqlalchemy import create_engine
import configparser

# Load DB config
config = configparser.ConfigParser()
config.read('config.ini')
db_url = config['postgresql']['db_url']

# 1. Extract
def extract_covid_data():
    url = 'https://api.covid19api.com/summary'
    response = requests.get(url)
    data = response.json()
    return data['Countries']

# 2. Transform
def transform(data):
    df = pd.DataFrame(data)
    # Select relevant columns
    df = df[['Country', 'TotalConfirmed', 'TotalDeaths', 'TotalRecovered', 'Date']]
    # Rename columns if needed
    df.columns = ['country', 'confirmed', 'deaths', 'recovered', 'date']
    return df

# 3. Load
def load(df):
    engine = create_engine(db_url)
    df.to_sql('covid_stats', engine, if_exists='replace', index=False)

def main():
    data = extract_covid_data()
    df = transform(data)
    load(df)
    print("ETL pipeline completed successfully.")

if __name__ == '__main__':
    main()
