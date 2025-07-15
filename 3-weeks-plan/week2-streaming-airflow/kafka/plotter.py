import json
import time
import matplotlib.pyplot as plt
import os

DUMP_FILENAME = 'memory_bootstrap.json'
CHART_FILENAME = 'market_prices.png'
INTERVAL = 600  # 10 minutes

def load_data(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r') as f:
        return json.load(f)

def get_latest_prices(data):
    latest_prices = {}
    for entry in data:
        asset = entry.get('asset')
        price = entry.get('price')
        if asset and price is not None:
            latest_prices[asset] = price
    return latest_prices

def plot_prices(latest_prices):
    if not latest_prices:
        print("No data to plot.")
        return

    assets = list(latest_prices.keys())
    prices = [latest_prices[a] for a in assets]
    plt.figure(figsize=(10,6))
    plt.bar(assets, prices, color='skyblue')
    plt.ylabel('Price')
    plt.xlabel('Asset')
    plt.title('Latest Prices per Asset')
    plt.tight_layout()
    plt.savefig(CHART_FILENAME)
    plt.close()
    print(f"Chart saved to {CHART_FILENAME}")

if __name__ == "__main__":
    while True:
        data = load_data(DUMP_FILENAME)
        latest_prices = get_latest_prices(data)
        plot_prices(latest_prices)
        # Optional: Show chart interactively
        # plt.show()
        time.sleep(INTERVAL)
