#!/usr/bin/env python3
"""
Enhanced Kafka Consumer for Market Data Processing
Consumes real-time market data with processing, aggregation, and storage
"""

import json
import time
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from collections import defaultdict, deque
import statistics
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import pandas as pd
from sqlalchemy import create_engine, text

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MarketDataProcessor:
    """Process and aggregate market data"""
    
    def __init__(self, window_size: int = 300):  # 5 minutes default
        self.window_size = window_size
        self.data_windows = defaultdict(lambda: deque(maxlen=100))  # Store last 100 data points per asset
        self.aggregated_data = {}
        
    def process_message(self, message: Dict) -> Dict:
        """Process a single market data message"""
        asset_key = f"{message['market']}_{message['asset']}"
        
        # Add to window
        self.data_windows[asset_key].append(message)
        
        # Calculate aggregations for this asset
        window_data = list(self.data_windows[asset_key])
        if len(window_data) > 1:
            prices = [float(msg['price']) for msg in window_data]
            volumes = [float(msg.get('volume', 0)) for msg in window_data if msg.get('volume')]
            
            aggregated = {
                'asset': message['asset'],
                'market': message['market'],
                'current_price': message['price'],
                'avg_price': round(statistics.mean(prices), 4),
                'min_price': min(prices),
                'max_price': max(prices),
                'price_std': round(statistics.stdev(prices) if len(prices) > 1 else 0, 4),
                'data_points': len(window_data),
                'avg_volume': round(statistics.mean(volumes), 2) if volumes else 0,
                'price_change': round(((prices[-1] - prices[0]) / prices[0]) * 100, 4) if prices[0] != 0 else 0,
                'timestamp': message['timestamp'],
                'processed_at': time.time()
            }
            
            self.aggregated_data[asset_key] = aggregated
            return aggregated
        
        return message


class MarketDataConsumer:
    """Enhanced market data consumer with processing and storage"""
    
    def __init__(self, config_file: str = None):
        """Initialize the consumer"""
        self.logger = self._setup_logging()
        self.config = self._load_config(config_file)
        
        # Initialize components
        self.consumer = self._create_consumer()
        self.processor = MarketDataProcessor(window_size=self.config['window_size'])
        self.database_engine = self._create_database_engine()
        
        # Storage and metrics
        self.message_buffer = []
        self.metrics = {
            'messages_consumed': 0,
            'messages_processed': 0,
            'messages_stored': 0,
            'processing_errors': 0,
            'last_commit': None,
            'start_time': time.time()
        }
        
        self.logger.info("Market Data Consumer initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        os.makedirs('logs', exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(f'logs/consumer_{datetime.now().strftime("%Y%m%d")}.log')
            ]
        )
        return logging.getLogger(__name__)
    
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from file or environment"""
        config = {
            'bootstrap_servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
            'topic': os.getenv('KAFKA_TOPIC', 'market-data'),
            'group_id': os.getenv('KAFKA_GROUP_ID', 'market-data-consumers'),
            'auto_offset_reset': os.getenv('KAFKA_AUTO_OFFSET_RESET', 'earliest'),
            'enable_auto_commit': os.getenv('KAFKA_AUTO_COMMIT', 'true').lower() == 'true',
            'auto_commit_interval_ms': int(os.getenv('KAFKA_AUTO_COMMIT_INTERVAL', '5000')),
            'max_poll_records': int(os.getenv('KAFKA_MAX_POLL_RECORDS', '100')),
            'session_timeout_ms': int(os.getenv('KAFKA_SESSION_TIMEOUT', '30000')),
            'window_size': int(os.getenv('PROCESSING_WINDOW_SIZE', '300')),
            'batch_size': int(os.getenv('STORAGE_BATCH_SIZE', '50')),
            'storage_interval': int(os.getenv('STORAGE_INTERVAL', '60')),
            'database_url': os.getenv('DATABASE_URL', 'postgresql://data_eng:password123@localhost:5432/data_engineering')
        }
        
        self.logger.info(f"Consumer configuration loaded: {config}")
        return config
    
    def _create_consumer(self) -> KafkaConsumer:
        """Create Kafka consumer with optimized settings"""
        try:
            consumer = KafkaConsumer(
                self.config['topic'],
                bootstrap_servers=self.config['bootstrap_servers'],
                group_id=self.config['group_id'],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                auto_offset_reset=self.config['auto_offset_reset'],
                enable_auto_commit=self.config['enable_auto_commit'],
                auto_commit_interval_ms=self.config['auto_commit_interval_ms'],
                max_poll_records=self.config['max_poll_records'],
                session_timeout_ms=self.config['session_timeout_ms'],
                consumer_timeout_ms=10000  # 10 second timeout for polling
            )
            
            self.logger.info(f"Kafka consumer created for topic: {self.config['topic']}")
            return consumer
            
        except Exception as e:
            self.logger.error(f"Failed to create Kafka consumer: {e}")
            raise
    
    def _create_database_engine(self):
        """Create database engine for data storage"""
        try:
            engine = create_engine(self.config['database_url'])
            
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.logger.info("Database connection established")
            return engine
            
        except Exception as e:
            self.logger.error(f"Failed to create database connection: {e}")
            return None
    
    def _create_tables(self):
        """Create required database tables"""
        if not self.database_engine:
            return
            
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS market_data_stream (
            id SERIAL PRIMARY KEY,
            asset VARCHAR(20) NOT NULL,
            market VARCHAR(50) NOT NULL,
            price DECIMAL(18,8) NOT NULL,
            volume DECIMAL(18,8),
            change_24h DECIMAL(8,4),
            bid DECIMAL(18,8),
            ask DECIMAL(18,8),
            timestamp BIGINT NOT NULL,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_asset_timestamp (asset, timestamp),
            INDEX idx_market (market),
            INDEX idx_received_at (received_at)
        );
        
        CREATE TABLE IF NOT EXISTS market_data_aggregated (
            id SERIAL PRIMARY KEY,
            asset VARCHAR(20) NOT NULL,
            market VARCHAR(50) NOT NULL,
            current_price DECIMAL(18,8),
            avg_price DECIMAL(18,8),
            min_price DECIMAL(18,8),
            max_price DECIMAL(18,8),
            price_std DECIMAL(18,8),
            avg_volume DECIMAL(18,8),
            price_change DECIMAL(8,4),
            data_points INTEGER,
            window_start TIMESTAMP,
            window_end TIMESTAMP,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_asset_processed (asset, processed_at),
            INDEX idx_market_processed (market, processed_at)
        );
        """
        
        try:
            with self.database_engine.connect() as conn:
                conn.execute(text(create_table_sql))
                conn.commit()
            self.logger.info("Database tables created/verified")
        except Exception as e:
            self.logger.error(f"Error creating database tables: {e}")
    
    def process_message(self, message: Dict) -> Optional[Dict]:
        """Process a single message"""
        try:
            # Validate message structure
            required_fields = ['market', 'asset', 'price', 'timestamp']
            if not all(field in message for field in required_fields):
                self.logger.warning(f"Message missing required fields: {message}")
                return None
            
            # Process through aggregator
            processed_data = self.processor.process_message(message)
            
            self.metrics['messages_processed'] += 1
            return processed_data
            
        except Exception as e:
            self.metrics['processing_errors'] += 1
            self.logger.error(f"Error processing message: {e}")
            return None
    
    def store_data(self, data_batch: List[Dict]):
        """Store processed data to database"""
        if not self.database_engine or not data_batch:
            return
        
        try:
            # Separate raw and aggregated data
            raw_data = []
            aggregated_data = []
            
            for item in data_batch:
                if 'avg_price' in item:  # This is aggregated data
                    aggregated_data.append({
                        'asset': item['asset'],
                        'market': item['market'],
                        'current_price': item['current_price'],
                        'avg_price': item['avg_price'],
                        'min_price': item['min_price'],
                        'max_price': item['max_price'],
                        'price_std': item['price_std'],
                        'avg_volume': item['avg_volume'],
                        'price_change': item['price_change'],
                        'data_points': item['data_points'],
                        'processed_at': datetime.fromtimestamp(item['processed_at'])
                    })
                else:  # This is raw data
                    raw_data.append({
                        'asset': item['asset'],
                        'market': item['market'],
                        'price': item['price'],
                        'volume': item.get('volume'),
                        'change_24h': item.get('change_24h'),
                        'bid': item.get('bid'),
                        'ask': item.get('ask'),
                        'timestamp': item['timestamp']
                    })
            
            # Store raw data
            if raw_data:
                df_raw = pd.DataFrame(raw_data)
                df_raw.to_sql('market_data_stream', self.database_engine, 
                             if_exists='append', index=False, method='multi')
                self.logger.debug(f"Stored {len(raw_data)} raw records")
            
            # Store aggregated data
            if aggregated_data:
                df_agg = pd.DataFrame(aggregated_data)
                df_agg.to_sql('market_data_aggregated', self.database_engine,
                             if_exists='append', index=False, method='multi')
                self.logger.debug(f"Stored {len(aggregated_data)} aggregated records")
            
            self.metrics['messages_stored'] += len(data_batch)
            
        except Exception as e:
            self.logger.error(f"Error storing data: {e}")
    
    def save_to_json(self, data_batch: List[Dict], filename: str = None):
        """Save data batch to JSON file as backup"""
        if not filename:
            filename = f"market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            os.makedirs('data/processed', exist_ok=True)
            filepath = os.path.join('data/processed', filename)
            
            with open(filepath, 'w') as f:
                json.dump(data_batch, f, indent=2, default=str)
            
            self.logger.info(f"Saved {len(data_batch)} records to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving to JSON: {e}")
    
    def consume_messages(self):
        """Main message consumption loop"""
        self.logger.info("Starting message consumption")
        
        # Create database tables
        self._create_tables()
        
        last_storage_time = time.time()
        
        try:
            for message in self.consumer:
                try:
                    # Process message
                    message_data = message.value
                    processed_data = self.process_message(message_data)
                    
                    if processed_data:
                        self.message_buffer.append(processed_data)
                    
                    self.metrics['messages_consumed'] += 1
                    
                    # Log progress periodically
                    if self.metrics['messages_consumed'] % 100 == 0:
                        self.log_metrics()
                    
                    # Store data periodically or when buffer is full
                    current_time = time.time()
                    if (len(self.message_buffer) >= self.config['batch_size'] or
                        (current_time - last_storage_time) >= self.config['storage_interval']):
                        
                        if self.message_buffer:
                            # Store to database
                            self.store_data(self.message_buffer.copy())
                            
                            # Also save to JSON as backup
                            self.save_to_json(self.message_buffer.copy())
                            
                            self.message_buffer.clear()
                            last_storage_time = current_time
                            
                            # Commit offset
                            if not self.config['enable_auto_commit']:
                                self.consumer.commit()
                                self.metrics['last_commit'] = datetime.now()
                
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")
                    continue
                    
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal, shutting down...")
        except Exception as e:
            self.logger.error(f"Unexpected error in consumption loop: {e}")
            raise
        finally:
            self.cleanup()
    
    def log_metrics(self):
        """Log current consumption metrics"""
        uptime = time.time() - self.metrics['start_time']
        messages_per_second = self.metrics['messages_consumed'] / uptime if uptime > 0 else 0
        
        self.logger.info(
            f"Metrics - Consumed: {self.metrics['messages_consumed']}, "
            f"Processed: {self.metrics['messages_processed']}, "
            f"Stored: {self.metrics['messages_stored']}, "
            f"Errors: {self.metrics['processing_errors']}, "
            f"Rate: {messages_per_second:.2f} msg/sec, "
            f"Buffer: {len(self.message_buffer)}, "
            f"Uptime: {uptime:.0f}s"
        )
    
    def get_consumer_lag(self) -> Dict:
        """Get consumer lag information"""
        try:
            # Get topic partitions
            partitions = self.consumer.partitions_for_topic(self.config['topic'])
            if not partitions:
                return {}
            
            lag_info = {}
            for partition in partitions:
                tp = TopicPartition(self.config['topic'], partition)
                
                # Get current position
                position = self.consumer.position(tp)
                
                # Get high water mark (latest offset)
                high_water_mark = self.consumer.end_offsets([tp])[tp]
                
                lag = high_water_mark - position
                lag_info[f'partition_{partition}'] = {
                    'position': position,
                    'high_water_mark': high_water_mark,
                    'lag': lag
                }
            
            return lag_info
            
        except Exception as e:
            self.logger.error(f"Error getting consumer lag: {e}")
            return {}
    
    def cleanup(self):
        """Cleanup resources"""
        self.logger.info("Cleaning up consumer resources")
        
        # Store any remaining buffered data
        if self.message_buffer:
            self.store_data(self.message_buffer)
            self.save_to_json(self.message_buffer)
        
        # Close consumer
        if self.consumer:
            self.consumer.close()
        
        # Close database connection
        if self.database_engine:
            self.database_engine.dispose()
        
        self.log_metrics()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Market Data Kafka Consumer")
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        consumer = MarketDataConsumer(config_file=args.config)
        consumer.consume_messages()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()