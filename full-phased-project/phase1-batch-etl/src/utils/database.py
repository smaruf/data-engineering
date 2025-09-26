"""
Database utilities
"""

import logging
from sqlalchemy import create_engine, text
from typing import Optional


class DatabaseManager:
    """Database management utilities"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine = create_engine(db_url)
        self.logger = logging.getLogger(__name__)
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            self.logger.info("Database connection successful")
            return True
        except Exception as e:
            self.logger.error(f"Database connection failed: {str(e)}")
            return False
    
    def execute_sql(self, sql: str) -> Optional[any]:
        """Execute SQL statement"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                conn.commit()
                return result
        except Exception as e:
            self.logger.error(f"SQL execution failed: {str(e)}")
            raise