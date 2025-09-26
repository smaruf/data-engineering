#!/usr/bin/env python3
"""
Main ETL Pipeline for Phase 1: Batch ETL
Extracts COVID-19 data, transforms it, and loads into PostgreSQL
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractors.covid_api import CovidAPIExtractor
from transformers.covid_transformer import CovidTransformer
from loaders.postgres_loader import PostgresLoader
from utils.logger import setup_logger
from utils.database import DatabaseManager
from utils.validators import DataValidator


class ETLPipeline:
    """Main ETL Pipeline class for orchestrating the data flow"""
    
    def __init__(self, config_path: str = None):
        """Initialize the ETL pipeline with configuration"""
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), '..', 'config', 'config.ini'
        )
        
        # Setup logging
        self.logger = setup_logger('etl_pipeline')
        
        # Initialize components
        self.extractor = CovidAPIExtractor(self.config_path)
        self.transformer = CovidTransformer(self.config_path)
        self.loader = PostgresLoader(self.config_path)
        self.validator = DataValidator()
        
        # Metrics tracking
        self.metrics = {
            'start_time': None,
            'end_time': None,
            'records_extracted': 0,
            'records_transformed': 0,
            'records_loaded': 0,
            'records_failed': 0,
            'errors': []
        }
    
    def extract(self) -> List[Dict]:
        """Extract data from COVID-19 APIs"""
        self.logger.info("Starting data extraction phase")
        
        try:
            # Extract data from multiple sources
            raw_data = []
            
            # Extract from disease.sh API
            disease_data = self.extractor.extract_disease_sh_data()
            if disease_data:
                raw_data.extend(disease_data)
                self.logger.info(f"Extracted {len(disease_data)} records from disease.sh")
            
            # Extract from other sources if configured
            # johns_hopkins_data = self.extractor.extract_johns_hopkins_data()
            # who_data = self.extractor.extract_who_data()
            
            self.metrics['records_extracted'] = len(raw_data)
            self.logger.info(f"Total extraction completed: {len(raw_data)} records")
            
            return raw_data
            
        except Exception as e:
            self.logger.error(f"Error during extraction: {str(e)}")
            self.metrics['errors'].append(f"Extraction error: {str(e)}")
            raise
    
    def transform(self, raw_data: List[Dict]) -> List[Dict]:
        """Transform the extracted data"""
        self.logger.info("Starting data transformation phase")
        
        try:
            if not raw_data:
                self.logger.warning("No data to transform")
                return []
            
            # Transform the data
            transformed_data = self.transformer.transform(raw_data)
            
            # Validate transformed data
            valid_records = []
            invalid_count = 0
            
            for record in transformed_data:
                if self.validator.validate_covid_record(record):
                    valid_records.append(record)
                else:
                    invalid_count += 1
                    self.logger.warning(f"Invalid record skipped: {record}")
            
            self.metrics['records_transformed'] = len(valid_records)
            self.metrics['records_failed'] = invalid_count
            
            self.logger.info(
                f"Transformation completed: {len(valid_records)} valid records, "
                f"{invalid_count} invalid records"
            )
            
            return valid_records
            
        except Exception as e:
            self.logger.error(f"Error during transformation: {str(e)}")
            self.metrics['errors'].append(f"Transformation error: {str(e)}")
            raise
    
    def load(self, transformed_data: List[Dict]) -> bool:
        """Load the transformed data into PostgreSQL"""
        self.logger.info("Starting data loading phase")
        
        try:
            if not transformed_data:
                self.logger.warning("No data to load")
                return True
            
            # Load data to database
            success = self.loader.load_data(transformed_data)
            
            if success:
                self.metrics['records_loaded'] = len(transformed_data)
                self.logger.info(f"Successfully loaded {len(transformed_data)} records")
            else:
                self.logger.error("Failed to load data to database")
                self.metrics['errors'].append("Data loading failed")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error during loading: {str(e)}")
            self.metrics['errors'].append(f"Loading error: {str(e)}")
            raise
    
    def run(self) -> bool:
        """Run the complete ETL pipeline"""
        self.logger.info("Starting ETL pipeline execution")
        self.metrics['start_time'] = datetime.now()
        
        try:
            # Extract
            raw_data = self.extract()
            
            # Transform
            transformed_data = self.transform(raw_data)
            
            # Load
            success = self.load(transformed_data)
            
            # Record completion
            self.metrics['end_time'] = datetime.now()
            self.log_metrics()
            
            if success:
                self.logger.info("ETL pipeline completed successfully")
                return True
            else:
                self.logger.error("ETL pipeline completed with errors")
                return False
                
        except Exception as e:
            self.metrics['end_time'] = datetime.now()
            self.logger.error(f"ETL pipeline failed: {str(e)}")
            self.log_metrics()
            return False
    
    def log_metrics(self):
        """Log pipeline execution metrics"""
        if self.metrics['start_time'] and self.metrics['end_time']:
            duration = self.metrics['end_time'] - self.metrics['start_time']
            self.metrics['duration_seconds'] = duration.total_seconds()
        
        self.logger.info("ETL Pipeline Metrics:", extra={'metrics': self.metrics})
        
        # Log summary
        self.logger.info(
            f"Pipeline Summary - "
            f"Extracted: {self.metrics['records_extracted']}, "
            f"Transformed: {self.metrics['records_transformed']}, "
            f"Loaded: {self.metrics['records_loaded']}, "
            f"Failed: {self.metrics['records_failed']}, "
            f"Duration: {self.metrics.get('duration_seconds', 0):.2f}s"
        )


def main():
    """Main entry point for the ETL pipeline"""
    parser = argparse.ArgumentParser(description="COVID-19 Data ETL Pipeline")
    parser.add_argument(
        '--config', 
        type=str, 
        help='Path to configuration file'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true', 
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize and run pipeline
    try:
        pipeline = ETLPipeline(config_path=args.config)
        success = pipeline.run()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()