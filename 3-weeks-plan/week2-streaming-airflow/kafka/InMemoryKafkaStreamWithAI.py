import os
import time
import random
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DB_CONN = sqlite3.connect(':memory:', check_same_thread=False)

ASSETS = ["USD/BDT", "EUR/USD", "BTC/USDT"]

def query_ollama(prompt, model="gemma"):
    url = f"{OLLAMA_HOST}/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()["response"]

def produce_data(n=30):
    for _ in range(n):
        trade = {
            "market": "LocalMoneyExchange",
            "asset": random.choice(ASSETS),
            "price": round(random.uniform(80, 120), 2),
            "volume": random.randint(100, 10000),
            "timestamp": int(time.time())
        }
        yield trade
        time.sleep(0.1)

def store_data(trade):
    df = pd.DataFrame([trade])
    df.to_sql('trades', DB_CONN, if_exists='append', index=False)

def load_data():
    return pd.read_sql("SELECT * FROM trades", DB_CONN)

def analyze_with_ai(df):
    prompt = (
        "Given the following JSON data of market trades, provide some meaningful insights. "
        "Data:\n" + df.to_json(orient="records")
    )
    return query_ollama(prompt, model="gemma")

def plot_charts(df):
    plt.figure(figsize=(12, 6))
    sns.barplot(x='asset', y='price', data=df, ci=None)
    plt.title('Average Price per Asset')
    plt.savefig('avg_price_per_asset.png')
    plt.clf()

    sns.barplot(x='asset', y='volume', data=df, ci=None)
    plt.title('Total Volume per Asset')
    plt.savefig('total_volume_per_asset.png')
    plt.clf()

    # Time series plot
    df['dt'] = pd.to_datetime(df['timestamp'], unit='s')
    for asset in df['asset'].unique():
        asset_df = df[df['asset'] == asset]
        plt.plot(asset_df['dt'], asset_df['price'], label=asset)
    plt.legend()
    plt.title('Price Over Time')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.savefig('price_over_time.png')
    plt.clf()

def main():
    # Stream, store, and collect data
    for trade in produce_data():
        store_data(trade)
    df = load_data()

    # Generate charts
    plot_charts(df)

    # Get AI insights
    print("Querying Ollama/Gemma for AI insights...")
    insights = analyze_with_ai(df)
    print("\n--- AI Market Insights ---")
    print(insights)

    print("\nCharts saved as:")
    print("  avg_price_per_asset.png")
    print("  total_volume_per_asset.png")
    print("  price_over_time.png")

if __name__ == "__main__":
    main()
