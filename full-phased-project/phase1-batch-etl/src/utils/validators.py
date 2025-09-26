"""
Data validation utilities
"""

from typing import Dict, Any
import logging


class DataValidator:
    """Data validation class for COVID-19 records"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_covid_record(self, record: Dict[str, Any]) -> bool:
        """Validate a COVID-19 data record"""
        
        # Required fields
        required_fields = ['country', 'confirmed', 'deaths', 'recovered']
        
        for field in required_fields:
            if field not in record:
                self.logger.warning(f"Missing required field: {field}")
                return False
            
            if record[field] is None:
                self.logger.warning(f"Null value in required field: {field}")
                return False
        
        # Validate country name
        if not isinstance(record['country'], str) or len(record['country'].strip()) == 0:
            self.logger.warning(f"Invalid country name: {record.get('country')}")
            return False
        
        # Validate numeric fields
        numeric_fields = ['confirmed', 'deaths', 'recovered', 'active']
        for field in numeric_fields:
            if field in record:
                if not isinstance(record[field], (int, float)) or record[field] < 0:
                    self.logger.warning(f"Invalid {field} value: {record.get(field)}")
                    return False
        
        # Logical validations
        confirmed = record.get('confirmed', 0)
        deaths = record.get('deaths', 0)
        recovered = record.get('recovered', 0)
        
        # Deaths shouldn't exceed confirmed cases
        if deaths > confirmed:
            self.logger.warning(f"Deaths ({deaths}) exceed confirmed cases ({confirmed})")
            return False
        
        # Recovered shouldn't exceed confirmed cases
        if recovered > confirmed:
            self.logger.warning(f"Recovered ({recovered}) exceed confirmed cases ({confirmed})")
            return False
        
        return True