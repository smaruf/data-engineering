import json
import time
import requests
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def fetch_binance_btcusdt():
    url = 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        return {
            "market": "Binance",
            "asset": "BTC/USDT",
            "price": float(data['price']),
            "timestamp": time.time()
        }
    except Exception:
        return None

def fetch_coinbase_ethusd():
    url = 'https://api.coinbase.com/v2/prices/ETH-USD/spot'
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        return {
            "market": "Coinbase",
            "asset": "ETH/USD",
            "price": float(data['data']['amount']),
            "timestamp": time.time()
        }
    except Exception:
        return None

def fetch_forex_eurusd():
    url = 'https://api.exchangerate.host/latest?base=EUR&symbols=USD'
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        return {
            "market": "Forex",
            "asset": "EUR/USD",
            "price": float(data['rates']['USD']),
            "timestamp": time.time()
        }
    except Exception:
        return None

def fetch_sample_trade_data():
    return {
        "market": "LocalMoneyExchange",
        "asset": "USD/BDT",
        "price": 110.35,
        "volume": 5000,
        "timestamp": time.time()
    }

while True:
    data_list = [
        fetch_binance_btcusdt(),
        fetch_coinbase_ethusd(),
        fetch_forex_eurusd(),
        fetch_sample_trade_data()
    ]
    for data in data_list:
        if data is not None:
            producer.send('money-market', value=data)
            print(f"Produced: {data}")
    time.sleep(600)  # 10 minutes interval
