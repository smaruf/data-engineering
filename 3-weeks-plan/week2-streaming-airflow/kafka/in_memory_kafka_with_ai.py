import os
import time
import threading
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DB_CONN = sqlite3.connect(':memory:', check_same_thread=False)

# ========== Exchange Data Collectors ==========

def fetch_forex_rates():
    url = "https://api.exchangerate.host/latest?base=USD&symbols=BDT,EUR"
    try:
        response = requests.get(url)
        data = response.json()
        rates = data.get("rates", {})
        return [
            {"market": "Forex", "asset": f"USD/{k}", "price": v, "volume": 1000, "timestamp": int(time.time())}
            for k, v in rates.items()
        ]
    except Exception as e:
        print(f"[Forex] Error: {e}")
        return []

def fetch_crypto_rates():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin,ethereum", "vs_currencies": "usd"}
    try:
        response = requests.get(url, params=params)
        data = response.json()
        results = []
        for coin in ["bitcoin", "ethereum"]:
            if coin in data:
                results.append({
                    "market": "Crypto",
                    "asset": f"{coin.upper()}/USD",
                    "price": data[coin]["usd"],
                    "volume": 1000,
                    "timestamp": int(time.time())
                })
        return results
    except Exception as e:
        print(f"[Crypto] Error: {e}")
        return []

# ========== AI Analysis ==========

def query_ollama(prompt, model="gemma"):
    url = f"{OLLAMA_HOST}/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        print(f"[Ollama] Error: {e}")
        return "AI analysis unavailable due to error."

# ========== In-Memory Kafka Broker ==========

class InMemoryKafkaBroker:
    def __init__(self):
        self.topics = {}
        self.active = False

    def start(self):
        self.active = True

    def stop(self):
        self.active = False

    def create_topic(self, topic):
        if topic not in self.topics:
            self.topics[topic] = []

    def send(self, topic, value):
        if not self.active:
            raise Exception("Broker not started")
        self.create_topic(topic)
        self.topics[topic].append(value)

    def consume(self, topic, timeout=5):
        self.create_topic(topic)
        start = time.time()
        while time.time() - start < timeout:
            if self.topics[topic]:
                return self.topics[topic].pop(0)
            time.sleep(0.1)
        return None

    def is_active(self):
        return self.active

# ========== Producer ==========

def producer(broker, topic, interval=60):
    while broker.is_active():
        forex_trades = fetch_forex_rates()
        for trade in forex_trades:
            broker.send(topic, json.dumps(trade))
            print("[Producer] Produced (forex):", trade)
        crypto_trades = fetch_crypto_rates()
        for trade in crypto_trades:
            broker.send(topic, json.dumps(trade))
            print("[Producer] Produced (crypto):", trade)
        time.sleep(interval)

# ========== Consumer, Storage, Charting, AI ==========

def store_data(trade):
    df = pd.DataFrame([trade])
    df.to_sql('trades', DB_CONN, if_exists='append', index=False)

def load_data():
    return pd.read_sql("SELECT * FROM trades", DB_CONN)

def plot_charts(df):
    if df.empty:
        print("No data to plot.")
        return
    plt.figure(figsize=(8, 4))
    df.groupby('asset')['price'].mean().plot(kind='bar')
    plt.title('Average Price per Asset')
    plt.ylabel('Average Price')
    plt.tight_layout()
    plt.savefig('avg_price_per_asset.png')
    plt.clf()

    df.groupby('asset')['volume'].sum().plot(kind='bar', color='orange')
    plt.title('Total Volume per Asset')
    plt.ylabel('Total Volume')
    plt.tight_layout()
    plt.savefig('total_volume_per_asset.png')
    plt.clf()

def consumer(broker, topic, poll_limit=10):
    i = 0
    while broker.is_active() and i < poll_limit:
        msg = broker.consume(topic)
        if msg:
            trade = json.loads(msg)
            print("[Consumer] Consumed:", trade)
            store_data(trade)
            i += 1
        else:
            time.sleep(1)
    print("[Consumer] Stopping after", i, "messages.")

    # ANALYZE AND PLOT
    df = load_data()
    plot_charts(df)
    if not df.empty:
        prompt = (
            "Given the following market trade data in JSON, provide meaningful insights about current forex and crypto trends. "
            "Consider price patterns, anomalies, or opportunities:\n"
            + df.to_json(orient="records")
        )
        insights = query_ollama(prompt, model="gemma")
        print("\n--- AI Market Insights ---\n", insights)
        print("\nCharts saved as:")
        print("  avg_price_per_asset.png")
        print("  total_volume_per_asset.png")

# ========== MAIN LOGIC ==========

if __name__ == "__main__":
    broker = InMemoryKafkaBroker()
    topic = "money-market"
    broker.start()

    prod_thread = threading.Thread(target=producer, args=(broker, topic, 60), daemon=True)
    cons_thread = threading.Thread(target=consumer, args=(broker, topic, 10), daemon=True)  # 10 messages per run

    prod_thread.start()
    cons_thread.start()

    try:
        input("Press Enter to stop (after first 10 messages and analysis)...\n")
    finally:
        broker.stop()
        prod_thread.join(timeout=2)
        cons_thread.join(timeout=2)
        print("[Main] Shutdown complete.")
