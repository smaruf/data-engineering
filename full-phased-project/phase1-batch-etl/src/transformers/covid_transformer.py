"""
COVID-19 Data Transformer
Handles data transformation and cleaning for COVID-19 data
"""

import pandas as pd
import logging
from typing import Dict, List
from datetime import datetime
import configparser


class CovidTransformer:
    """Transformer for COVID-19 data"""
    
    def __init__(self, config_path: str):
        """Initialize the transformer with configuration"""
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        self.logger = logging.getLogger(__name__)
    
    def transform(self, raw_data: List[Dict]) -> List[Dict]:
        """Transform raw COVID-19 data"""
        self.logger.info(f"Starting transformation of {len(raw_data)} records")
        
        if not raw_data:
            return []
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(raw_data)
        
        # Apply transformations
        df = self._clean_data(df)
        df = self._standardize_columns(df)
        df = self._add_calculated_fields(df)
        df = self._handle_missing_values(df)
        
        # Convert back to list of dictionaries
        transformed_data = df.to_dict('records')
        
        self.logger.info(f"Transformation completed: {len(transformed_data)} records")
        return transformed_data
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean the data by removing duplicates and invalid entries"""
        self.logger.debug("Cleaning data")
        
        # Remove duplicates based on country
        initial_count = len(df)
        df = df.drop_duplicates(subset=['country'], keep='last')
        duplicates_removed = initial_count - len(df)
        
        if duplicates_removed > 0:
            self.logger.info(f"Removed {duplicates_removed} duplicate records")
        
        # Remove records with invalid country names
        df = df[df['country'].notna()]
        df = df[df['country'] != '']
        df = df[df['country'] != 'Unknown']
        
        return df
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names and data types"""
        self.logger.debug("Standardizing columns")
        
        # Ensure numeric columns are properly typed
        numeric_columns = [
            'confirmed', 'deaths', 'recovered', 'active', 'critical',
            'cases_per_million', 'deaths_per_million', 'tests', 
            'tests_per_million', 'population'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Standardize country names
        df['country'] = df['country'].str.strip()
        df['country'] = df['country'].str.title()
        
        # Handle date columns
        if 'updated' in df.columns:
            df['updated'] = pd.to_datetime(df['updated'], unit='ms', errors='coerce')
        
        if 'extracted_at' in df.columns:
            df['extracted_at'] = pd.to_datetime(df['extracted_at'], errors='coerce')
        
        return df
    
    def _add_calculated_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add calculated fields for analytics"""
        self.logger.debug("Adding calculated fields")
        
        # Calculate case fatality rate
        df['case_fatality_rate'] = (
            df['deaths'] / df['confirmed'].replace(0, 1) * 100
        ).round(2)
        
        # Calculate recovery rate
        df['recovery_rate'] = (
            df['recovered'] / df['confirmed'].replace(0, 1) * 100
        ).round(2)
        
        # Calculate active case rate
        df['active_rate'] = (
            df['active'] / df['confirmed'].replace(0, 1) * 100
        ).round(2)
        
        # Add processing timestamp
        df['processed_at'] = datetime.now()
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values appropriately"""
        self.logger.debug("Handling missing values")
        
        # Fill missing numeric values with 0
        numeric_columns = df.select_dtypes(include=['number']).columns
        df[numeric_columns] = df[numeric_columns].fillna(0)
        
        # Fill missing string values
        string_columns = df.select_dtypes(include=['object']).columns
        for col in string_columns:
            if col in ['continent', 'country_code']:
                df[col] = df[col].fillna('Unknown')
        
        return df