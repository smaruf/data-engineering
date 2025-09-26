"""
COVID-19 API Data Extractor
Handles extraction of COVID-19 data from various public APIs
"""

import requests
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime
import configparser
import os


class CovidAPIExtractor:
    """Extractor for COVID-19 data from public APIs"""
    
    def __init__(self, config_path: str):
        """Initialize the extractor with configuration"""
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        self.logger = logging.getLogger(__name__)
        
        # API configuration
        self.base_url = self.config.get('api', 'covid_api_url', 
                                       fallback='https://disease.sh/v3/covid-19')
        self.rate_limit = self.config.getint('api', 'rate_limit', fallback=10)
        self.timeout = self.config.getint('api', 'timeout', fallback=30)
        self.retries = self.config.getint('api', 'retries', fallback=3)
        
        # Request session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'COVID-ETL-Pipeline/1.0'
        })
        
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Implement rate limiting for API requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.rate_limit
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Make an HTTP request with retry logic and rate limiting"""
        self._rate_limit()
        
        for attempt in range(self.retries):
            try:
                self.logger.debug(f"Making request to {url} (attempt {attempt + 1})")
                
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(
                    f"Request failed (attempt {attempt + 1}/{self.retries}): {str(e)}"
                )
                
                if attempt < self.retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"All retry attempts failed for {url}")
                    raise
        
        return None
    
    def extract_disease_sh_data(self) -> List[Dict]:
        """Extract data from disease.sh API"""
        self.logger.info("Extracting data from disease.sh API")
        
        try:
            # Get countries data
            countries_url = f"{self.base_url}/countries"
            countries_data = self._make_request(countries_url)
            
            if not countries_data:
                self.logger.error("Failed to extract countries data")
                return []
            
            # Format data for consistency
            formatted_data = []
            timestamp = datetime.now().isoformat()
            
            for country in countries_data:
                record = {
                    'source': 'disease.sh',
                    'country': country.get('country', 'Unknown'),
                    'country_code': country.get('countryInfo', {}).get('iso2'),
                    'confirmed': country.get('cases', 0),
                    'deaths': country.get('deaths', 0),
                    'recovered': country.get('recovered', 0),
                    'active': country.get('active', 0),
                    'critical': country.get('critical', 0),
                    'cases_per_million': country.get('casesPerOneMillion', 0),
                    'deaths_per_million': country.get('deathsPerOneMillion', 0),
                    'tests': country.get('tests', 0),
                    'tests_per_million': country.get('testsPerOneMillion', 0),
                    'population': country.get('population', 0),
                    'continent': country.get('continent'),
                    'updated': country.get('updated'),
                    'extracted_at': timestamp
                }
                formatted_data.append(record)
            
            self.logger.info(f"Successfully extracted {len(formatted_data)} records")
            return formatted_data
            
        except Exception as e:
            self.logger.error(f"Error extracting disease.sh data: {str(e)}")
            raise