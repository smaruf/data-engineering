import threading
import queue
import time
import random
import json

class InMemoryKafkaBroker:
    def __init__(self):
        self.topics = {}
        self.active = False
        self.lock = threading.Lock()

    def start(self):
        with self.lock:
            self.active = True
            print("[InMemoryKafkaBroker] Started.")

    def stop(self):
        with self.lock:
            self.active = False
            print("[InMemoryKafkaBroker] Stopped.")

    def create_topic(self, topic):
        with self.lock:
            if topic not in self.topics:
                self.topics[topic] = queue.Queue()

    def send(self, topic, value):
        with self.lock:
            if not self.active:
                raise RuntimeError("Broker not started.")
            self.create_topic(topic)
            self.topics[topic].put(value)

    def consume(self, topic, timeout=1):
        with self.lock:
            if not self.active:
                raise RuntimeError("Broker not started.")
            self.create_topic(topic)
        try:
            return self.topics[topic].get(timeout=timeout)
        except queue.Empty:
            return None

# Producer function
def money_exchange_producer(broker, topic, interval=10):
    assets = ['USD/BDT', 'EUR/USD', 'BTC/USDT']
    try:
        while broker.active:
            trade = {
                "market": "LocalMoneyExchange",
                "asset": random.choice(assets),
                "price": round(random.uniform(80, 120), 2),
                "volume": random.randint(100, 10000),
                "timestamp": time.time()
            }
            broker.send(topic, json.dumps(trade))
            print(f"[Producer] Produced: {trade}")
            time.sleep(interval)  # 10 seconds for demo; use 600 for 10 minutes
    except Exception as e:
        print("[Producer] Exception:", e)

# Consumer function
def money_exchange_consumer(broker, topic, dump_file="memory_bootstrap.json"):
    memory_data = []
    try:
        while broker.active:
            msg = broker.consume(topic, timeout=5)
            if msg:
                trade = json.loads(msg)
                print(f"[Consumer] Consumed: {trade}")
                memory_data.append(trade)
                # Dump to file after each message for demo
                with open(dump_file, "w") as f:
                    json.dump(memory_data, f, indent=2)
            else:
                time.sleep(1)
    except Exception as e:
        print("[Consumer] Exception:", e)

# Main integration
if __name__ == "__main__":
    broker = InMemoryKafkaBroker()
    topic = "money-market"

    # Start broker
    broker.start()

    # Start producer and consumer as threads
    producer_thread = threading.Thread(target=money_exchange_producer, args=(broker, topic, 10), daemon=True)
    consumer_thread = threading.Thread(target=money_exchange_consumer, args=(broker, topic, "memory_bootstrap.json"), daemon=True)
    producer_thread.start()
    consumer_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Main] Stopping broker and threads...")
        broker.stop()
        # Threads will exit as broker.active becomes False
        producer_thread.join(timeout=2)
        consumer_thread.join(timeout=2)
        print("[Main] Shutdown complete.")
