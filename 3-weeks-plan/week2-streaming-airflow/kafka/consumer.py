import json
from kafka import KafkaConsumer
from datetime import datetime

memory_data = []

consumer = KafkaConsumer(
    'money-market',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

DUMP_INTERVAL = 1  # Dump after every message (since producer is every 10min)
DUMP_FILENAME = 'memory_bootstrap.json'

def dump_memory_to_json():
    with open(DUMP_FILENAME, 'w') as f:
        json.dump(memory_data, f, indent=2)
    print(f"[{datetime.now()}] Dumped {len(memory_data)} records to {DUMP_FILENAME}")

msg_count = 0
for message in consumer:
    market_data = message.value
    print(f"Consumed: {market_data}")
    memory_data.append(market_data)
    msg_count += 1
    if msg_count % DUMP_INTERVAL == 0:
        dump_memory_to_json()
