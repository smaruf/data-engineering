import json
import matplotlib.pyplot as plt
from datetime import datetime

def plot_covid_data():
    log_path = '/tmp/covid_daily_log.jsonl'
    # Read all daily records
    records = []
    with open(log_path, 'r') as f:
        for line in f:
            record = json.loads(line)
            records.append(record)
    if not records:
        print("No records to plot.")
        return

    # Prepare data for plotting
    dates = [datetime.fromtimestamp(rec['updated']/1000).strftime('%Y-%m-%d') for rec in records]
    cases = [rec['cases'] for rec in records]
    deaths = [rec['deaths'] for rec in records]
    recovered = [rec['recovered'] for rec in records]

    x = range(len(dates))
    width = 0.25

    plt.figure(figsize=(12, 7))
    plt.bar([i - width for i in x], cases, width=width, label='Cases', color='blue')
    plt.bar(x, deaths, width=width, label='Deaths', color='red')
    plt.bar([i + width for i in x], recovered, width=width, label='Recovered', color='green')
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.title("COVID-19 Daily Summary")
    plt.xticks(x, dates, rotation=45)
    plt.legend()
    plt.tight_layout()
    plot_path = '/tmp/covid_daily_plot.png'
    plt.savefig(plot_path)
    plt.close()
    print(f"Saved COVID-19 daily bar chart to {plot_path}")
