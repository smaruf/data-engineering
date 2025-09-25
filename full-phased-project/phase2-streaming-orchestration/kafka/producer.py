#!/usr/bin/env python3
"""
Enhanced Kafka Producer for Market Data Streaming
Streams real-time market data from multiple sources with error handling and monitoring
"""

import json
import time
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError
import requests
from dataclasses import dataclass, asdict

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class MarketData:
    """Market data structure"""
    market: str
    asset: str
    price: float
    volume: Optional[float] = None
    timestamp: float = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    change_24h: Optional[float] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class MarketDataProducer:
    """Enhanced market data producer with multiple data sources"""
    
    def __init__(self, config_file: str = None):
        """Initialize the producer"""
        self.logger = self._setup_logging()
        self.config = self._load_config(config_file)
        
        # Initialize Kafka producer
        self.producer = self._create_producer()
        
        # Data source URLs
        self.data_sources = {
            'binance': 'https://api.binance.com/api/v3/ticker/24hr',
            'coinbase': 'https://api.coinbase.com/v2/exchange-rates',
            'forex': 'https://api.exchangerate.host/latest',
            'coingecko': 'https://api.coingecko.com/api/v3/simple/price'
        }
        
        # Metrics tracking
        self.metrics = {
            'messages_sent': 0,
            'messages_failed': 0,
            'sources_success': 0,
            'sources_failed': 0,
            'last_success': None
        }
        
        self.logger.info("Market Data Producer initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(f'logs/producer_{datetime.now().strftime("%Y%m%d")}.log')
            ]
        )
        return logging.getLogger(__name__)
    
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from file or environment"""
        config = {
            'bootstrap_servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
            'topic': os.getenv('KAFKA_TOPIC', 'market-data'),
            'batch_size': int(os.getenv('KAFKA_BATCH_SIZE', '16384')),
            'linger_ms': int(os.getenv('KAFKA_LINGER_MS', '100')),
            'compression_type': os.getenv('KAFKA_COMPRESSION', 'snappy'),
            'retries': int(os.getenv('KAFKA_RETRIES', '3')),
            'request_timeout_ms': int(os.getenv('KAFKA_REQUEST_TIMEOUT', '30000')),
            'api_timeout': int(os.getenv('API_TIMEOUT', '10')),
            'production_interval': int(os.getenv('PRODUCTION_INTERVAL', '60'))
        }
        
        self.logger.info(f"Configuration loaded: {config}")
        return config
    
    def _create_producer(self) -> KafkaProducer:
        """Create Kafka producer with optimized settings"""
        try:
            producer = KafkaProducer(
                bootstrap_servers=self.config['bootstrap_servers'],
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8') if k else None,
                batch_size=self.config['batch_size'],
                linger_ms=self.config['linger_ms'],
                compression_type=self.config['compression_type'],
                retries=self.config['retries'],
                request_timeout_ms=self.config['request_timeout_ms'],
                acks='all'  # Wait for all replicas to acknowledge
            )
            
            self.logger.info("Kafka producer created successfully")
            return producer
            
        except Exception as e:
            self.logger.error(f"Failed to create Kafka producer: {e}")
            raise
    
    def fetch_binance_data(self) -> List[MarketData]:
        """Fetch data from Binance API"""
        try:
            symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT']
            market_data = []
            
            for symbol in symbols:
                url = f"{self.data_sources['binance']}?symbol={symbol}"
                response = requests.get(url, timeout=self.config['api_timeout'])
                response.raise_for_status()
                
                data = response.json()
                market_data.append(MarketData(
                    market='Binance',
                    asset=f"{symbol[:3]}/{symbol[3:]}",
                    price=float(data['lastPrice']),
                    volume=float(data['volume']),
                    change_24h=float(data['priceChangePercent'])
                ))
            
            self.logger.debug(f"Fetched {len(market_data)} records from Binance")
            return market_data
            
        except Exception as e:
            self.logger.error(f"Error fetching Binance data: {e}")
            return []
    
    def fetch_coinbase_data(self) -> List[MarketData]:
        """Fetch data from Coinbase API"""
        try:
            response = requests.get(
                self.data_sources['coinbase'], 
                timeout=self.config['api_timeout']
            )
            response.raise_for_status()
            
            data = response.json()
            rates = data['data']['rates']
            
            market_data = []
            for currency in ['EUR', 'GBP', 'JPY', 'BTC', 'ETH']:
                if currency in rates:
                    market_data.append(MarketData(
                        market='Coinbase',
                        asset=f'USD/{currency}',
                        price=float(rates[currency])
                    ))
            
            self.logger.debug(f"Fetched {len(market_data)} records from Coinbase")
            return market_data
            
        except Exception as e:
            self.logger.error(f"Error fetching Coinbase data: {e}")
            return []
    
    def fetch_forex_data(self) -> List[MarketData]:
        """Fetch forex data"""
        try:
            base_currencies = ['USD', 'EUR', 'GBP']
            market_data = []
            
            for base in base_currencies:
                url = f"{self.data_sources['forex']}?base={base}&symbols=USD,EUR,GBP,JPY,CAD"
                response = requests.get(url, timeout=self.config['api_timeout'])
                response.raise_for_status()
                
                data = response.json()
                rates = data.get('rates', {})
                
                for target, rate in rates.items():
                    if base != target:  # Skip same currency
                        market_data.append(MarketData(
                            market='Forex',
                            asset=f'{base}/{target}',
                            price=float(rate)
                        ))
            
            self.logger.debug(f"Fetched {len(market_data)} forex records")
            return market_data
            
        except Exception as e:
            self.logger.error(f"Error fetching forex data: {e}")
            return []
    
    def fetch_crypto_data(self) -> List[MarketData]:
        """Fetch cryptocurrency data from CoinGecko"""
        try:
            params = {
                'ids': 'bitcoin,ethereum,cardano,polkadot,chainlink',
                'vs_currencies': 'usd',
                'include_24hr_change': 'true'
            }
            
            response = requests.get(
                self.data_sources['coingecko'],
                params=params,
                timeout=self.config['api_timeout']
            )
            response.raise_for_status()
            
            data = response.json()
            market_data = []
            
            coin_mapping = {
                'bitcoin': 'BTC',
                'ethereum': 'ETH',
                'cardano': 'ADA',
                'polkadot': 'DOT',
                'chainlink': 'LINK'
            }
            
            for coin_id, coin_data in data.items():
                if coin_id in coin_mapping:
                    market_data.append(MarketData(
                        market='CoinGecko',
                        asset=f"{coin_mapping[coin_id]}/USD",
                        price=float(coin_data['usd']),
                        change_24h=coin_data.get('usd_24h_change')
                    ))
            
            self.logger.debug(f"Fetched {len(market_data)} crypto records")
            return market_data
            
        except Exception as e:
            self.logger.error(f"Error fetching crypto data: {e}")
            return []
    
    def send_message(self, data: MarketData, key: str = None) -> bool:
        """Send market data to Kafka topic"""
        try:
            # Convert to dictionary for JSON serialization
            message = asdict(data)
            
            # Send message
            future = self.producer.send(
                self.config['topic'],
                key=key or f"{data.market}_{data.asset}",
                value=message
            )
            
            # Wait for acknowledgment (with timeout)
            record_metadata = future.get(timeout=10)
            
            self.metrics['messages_sent'] += 1
            self.metrics['last_success'] = datetime.now()
            
            self.logger.debug(
                f"Message sent to {record_metadata.topic} "
                f"partition {record_metadata.partition} "
                f"offset {record_metadata.offset}"
            )
            
            return True
            
        except KafkaError as e:
            self.metrics['messages_failed'] += 1
            self.logger.error(f"Kafka error sending message: {e}")
            return False
        except Exception as e:
            self.metrics['messages_failed'] += 1
            self.logger.error(f"Error sending message: {e}")
            return False
    
    def produce_batch(self) -> int:
        """Produce a batch of market data"""
        self.logger.info("Starting batch production")
        
        all_data = []
        sources_attempted = 0
        sources_successful = 0
        
        # Fetch from all sources
        data_fetchers = [
            ('Binance', self.fetch_binance_data),
            ('Coinbase', self.fetch_coinbase_data),
            ('Forex', self.fetch_forex_data),
            ('CoinGecko', self.fetch_crypto_data)
        ]
        
        for source_name, fetcher in data_fetchers:
            sources_attempted += 1
            try:
                data = fetcher()
                if data:
                    all_data.extend(data)
                    sources_successful += 1
                    self.logger.info(f"Successfully fetched {len(data)} records from {source_name}")
                else:
                    self.logger.warning(f"No data received from {source_name}")
            except Exception as e:
                self.logger.error(f"Failed to fetch from {source_name}: {e}")
        
        # Send messages
        messages_sent = 0
        for data in all_data:
            if self.send_message(data):
                messages_sent += 1
        
        # Update metrics
        self.metrics['sources_success'] += sources_successful
        self.metrics['sources_failed'] += (sources_attempted - sources_successful)
        
        # Ensure all messages are sent
        self.producer.flush()
        
        self.logger.info(
            f"Batch completed: {messages_sent}/{len(all_data)} messages sent "
            f"from {sources_successful}/{sources_attempted} sources"
        )
        
        return messages_sent
    
    def run_continuous(self):
        """Run producer continuously"""
        self.logger.info("Starting continuous production")
        
        try:
            while True:
                start_time = time.time()
                
                # Produce batch
                messages_sent = self.produce_batch()
                
                # Log metrics periodically
                if self.metrics['messages_sent'] % 100 == 0:
                    self.log_metrics()
                
                # Calculate sleep time
                elapsed = time.time() - start_time
                sleep_time = max(0, self.config['production_interval'] - elapsed)
                
                if sleep_time > 0:
                    self.logger.debug(f"Sleeping for {sleep_time:.2f} seconds")
                    time.sleep(sleep_time)
                else:
                    self.logger.warning("Production cycle took longer than interval")
                    
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal, shutting down...")
        except Exception as e:
            self.logger.error(f"Unexpected error in continuous production: {e}")
            raise
        finally:
            self.cleanup()
    
    def log_metrics(self):
        """Log current metrics"""
        success_rate = (
            self.metrics['messages_sent'] / 
            (self.metrics['messages_sent'] + self.metrics['messages_failed'])
        ) * 100 if (self.metrics['messages_sent'] + self.metrics['messages_failed']) > 0 else 0
        
        self.logger.info(
            f"Metrics - Messages: {self.metrics['messages_sent']} sent, "
            f"{self.metrics['messages_failed']} failed (Success rate: {success_rate:.1f}%), "
            f"Sources: {self.metrics['sources_success']} successful, "
            f"{self.metrics['sources_failed']} failed, "
            f"Last success: {self.metrics['last_success']}"
        )
    
    def cleanup(self):
        """Cleanup resources"""
        self.logger.info("Cleaning up producer resources")
        if self.producer:
            self.producer.flush()
            self.producer.close()
        self.log_metrics()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Market Data Kafka Producer")
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--once', action='store_true', help='Run once instead of continuously')
    
    args = parser.parse_args()
    
    try:
        producer = MarketDataProducer(config_file=args.config)
        
        if args.once:
            producer.produce_batch()
        else:
            producer.run_continuous()
            
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()