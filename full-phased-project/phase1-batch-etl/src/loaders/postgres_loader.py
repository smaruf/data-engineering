"""
PostgreSQL Data Loader
Handles loading of transformed data into PostgreSQL database
"""

import pandas as pd
import logging
from typing import Dict, List
from sqlalchemy import create_engine, text
import configparser
import os


class PostgresLoader:
    """Loader for PostgreSQL database"""
    
    def __init__(self, config_path: str):
        """Initialize the loader with configuration"""
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        self.logger = logging.getLogger(__name__)
        
        # Get database URL from config or environment
        self.db_url = (
            os.getenv('DATABASE_URL') or 
            self._build_db_url()
        )
        
        # Create database engine
        self.engine = create_engine(self.db_url)
    
    def _build_db_url(self) -> str:
        """Build database URL from configuration"""
        host = self.config.get('postgresql', 'host', fallback='localhost')
        port = self.config.get('postgresql', 'port', fallback='5432')
        database = self.config.get('postgresql', 'database', fallback='data_engineering')
        username = self.config.get('postgresql', 'username', fallback='data_eng')
        password = self.config.get('postgresql', 'password', fallback='password123')
        
        return f"postgresql://{username}:{password}@{host}:{port}/{database}"
    
    def load_data(self, data: List[Dict], table_name: str = 'covid_stats') -> bool:
        """Load data into PostgreSQL table"""
        self.logger.info(f"Loading {len(data)} records to table {table_name}")
        
        try:
            if not data:
                self.logger.warning("No data to load")
                return True
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Load data to database
            df.to_sql(
                table_name,
                self.engine,
                if_exists='replace',
                index=False,
                method='multi',
                chunksize=1000
            )
            
            self.logger.info(f"Successfully loaded {len(data)} records")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            return False
    
    def create_tables(self):
        """Create required database tables"""
        self.logger.info("Creating database tables")
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS covid_stats (
            id SERIAL PRIMARY KEY,
            source VARCHAR(50),
            country VARCHAR(100) NOT NULL,
            country_code VARCHAR(10),
            confirmed INTEGER DEFAULT 0,
            deaths INTEGER DEFAULT 0,
            recovered INTEGER DEFAULT 0,
            active INTEGER DEFAULT 0,
            critical INTEGER DEFAULT 0,
            cases_per_million DECIMAL(10,2) DEFAULT 0,
            deaths_per_million DECIMAL(10,2) DEFAULT 0,
            tests BIGINT DEFAULT 0,
            tests_per_million DECIMAL(10,2) DEFAULT 0,
            population BIGINT DEFAULT 0,
            continent VARCHAR(50),
            case_fatality_rate DECIMAL(5,2) DEFAULT 0,
            recovery_rate DECIMAL(5,2) DEFAULT 0,
            active_rate DECIMAL(5,2) DEFAULT 0,
            updated TIMESTAMP,
            extracted_at TIMESTAMP,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_covid_stats_country ON covid_stats(country);
        CREATE INDEX IF NOT EXISTS idx_covid_stats_continent ON covid_stats(continent);
        CREATE INDEX IF NOT EXISTS idx_covid_stats_extracted_at ON covid_stats(extracted_at);
        """
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(create_table_sql))
                conn.commit()
            
            self.logger.info("Database tables created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating tables: {str(e)}")
            raise