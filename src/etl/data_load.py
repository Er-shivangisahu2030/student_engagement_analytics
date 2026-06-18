"""
Data Loading Module
Handles loading transformed data into MySQL database.
"""

import pandas as pd
import logging
from typing import Dict
from sqlalchemy import create_engine, text

from database.connection import db_connection
from config import DB_CONFIG, ETL_CONFIG
from utils.helpers import chunk_dataframe


logger = logging.getLogger(__name__)


class DataLoader:
    """
    Loads transformed data into MySQL database.
    """
    
    def __init__(self, data: Dict[str, pd.DataFrame], db=None):
        """
        Initialize loader with transformed data.
        
        Args:
            data: Dictionary of DataFrames to load
            db: Database connection object
        """
        self.data = data
        self.db = db or db_connection
        self.load_stats = {}
        self._init_engine()
    
    def _init_engine(self):
        """Initialize SQLAlchemy engine for bulk operations."""
        try:
            connection_string = (
                f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
                f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
            )
            self.engine = create_engine(
                connection_string,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )
            logger.info("SQLAlchemy engine initialized")
        except Exception as e:
            logger.error(f"Error initializing SQLAlchemy engine: {str(e)}")
            raise
    
    def load_dim_student(self) -> int:
        """
        Load student dimension table.
        
        Returns:
            Number of rows loaded
        """
        logger.info("Loading dim_student...")
        try:
            df = self.data['dim_student']
            
            # Truncate existing data
            if self.db.table_exists('dim_student'):
                self.db.truncate_table('dim_student')
            
            # Load using SQLAlchemy for better performance
            rows_loaded = df.to_sql('dim_student', con=self.engine, if_exists='append', index=False, chunksize=ETL_CONFIG['batch_size'])
            
            self.load_stats['dim_student'] = {
                'rows_loaded': len(df),
                'status': 'SUCCESS'
            }
            
            logger.info(f"✓ Loaded dim_student: {len(df)} rows")
            return len(df)
        except Exception as e:
            logger.error(f"✗ Error loading dim_student: {str(e)}")
            self.load_stats['dim_student'] = {'status': 'FAILED', 'error': str(e)}
            raise
    
    def load_dim_course(self) -> int:
        """
        Load course dimension table.
        
        Returns:
            Number of rows loaded
        """
        logger.info("Loading dim_course...")
        try:
            df = self.data['dim_course']
            
            # Truncate existing data
            if self.db.table_exists('dim_course'):
                self.db.truncate_table('dim_course')
            
            # Load data
            rows_loaded = df.to_sql('dim_course', con=self.engine, if_exists='append', index=False, chunksize=ETL_CONFIG['batch_size'])
            
            self.load_stats['dim_course'] = {
                'rows_loaded': len(df),
                'status': 'SUCCESS'
            }
            
            logger.info(f"✓ Loaded dim_course: {len(df)} rows")
            return len(df)
        except Exception as e:
            logger.error(f"✗ Error loading dim_course: {str(e)}")
            self.load_stats['dim_course'] = {'status': 'FAILED', 'error': str(e)}
            raise
    
    def load_dim_assessment(self) -> int:
        """
        Load assessment dimension table.
        
        Returns:
            Number of rows loaded
        """
        logger.info("Loading dim_assessment...")
        try:
            df = self.data['dim_assessment']
            
            # Truncate existing data
            if self.db.table_exists('dim_assessment'):
                self.db.truncate_table('dim_assessment')
            
            # Load data
            rows_loaded = df.to_sql('dim_assessment', con=self.engine, if_exists='append', index=False, chunksize=ETL_CONFIG['batch_size'])
            
            self.load_stats['dim_assessment'] = {
                'rows_loaded': len(df),
                'status': 'SUCCESS'
            }
            
            logger.info(f"✓ Loaded dim_assessment: {len(df)} rows")
            return len(df)
        except Exception as e:
            logger.error(f"✗ Error loading dim_assessment: {str(e)}")
            self.load_stats['dim_assessment'] = {'status': 'FAILED', 'error': str(e)}
            raise
    
    def load_fact_assessment(self) -> int:
        """
        Load assessment fact table.
        
        Returns:
            Number of rows loaded
        """
        logger.info("Loading fact_assessment...")
        try:
            df = self.data['fact_assessment']
            
            # Truncate existing data
            if self.db.table_exists('fact_assessment'):
                self.db.truncate_table('fact_assessment')
            
            # Load data
            rows_loaded = df.to_sql('fact_assessment', con=self.engine, if_exists='append', index=False, chunksize=ETL_CONFIG['batch_size'])
            
            self.load_stats['fact_assessment'] = {
                'rows_loaded': len(df),
                'status': 'SUCCESS'
            }
            
            logger.info(f"✓ Loaded fact_assessment: {len(df)} rows")
            return len(df)
        except Exception as e:
            logger.error(f"✗ Error loading fact_assessment: {str(e)}")
            self.load_stats['fact_assessment'] = {'status': 'FAILED', 'error': str(e)}
            raise
    
    def load_fact_learning_activity(self) -> int:
        """
        Load learning activity fact table.
        
        Returns:
            Number of rows loaded
        """
        logger.info("Loading fact_learning_activity...")
        try:
            df = self.data['fact_learning_activity']
            
            # Truncate existing data
            if self.db.table_exists('fact_learning_activity'):
                self.db.truncate_table('fact_learning_activity')
            
            # Load data in chunks for large dataset
            total_rows = 0
            for chunk in chunk_dataframe(df, chunk_size=ETL_CONFIG['chunk_size']):
                chunk.to_sql('fact_learning_activity', con=self.engine, if_exists='append', index=False)
                total_rows += len(chunk)
                logger.info(f"  Loaded {total_rows}/{len(df)} rows...")
            
            self.load_stats['fact_learning_activity'] = {
                'rows_loaded': len(df),
                'status': 'SUCCESS'
            }
            
            logger.info(f"✓ Loaded fact_learning_activity: {len(df)} rows")
            return len(df)
        except Exception as e:
            logger.error(f"✗ Error loading fact_learning_activity: {str(e)}")
            self.load_stats['fact_learning_activity'] = {'status': 'FAILED', 'error': str(e)}
            raise
    
    def load_fact_engagement(self) -> int:
        """
        Load engagement fact table.
        
        Returns:
            Number of rows loaded
        """
        logger.info("Loading fact_engagement...")
        try:
            df = self.data['fact_engagement']
            
            # Truncate existing data
            if self.db.table_exists('fact_engagement'):
                self.db.truncate_table('fact_engagement')
            
            # Load data
            rows_loaded = df.to_sql('fact_engagement', con=self.engine, if_exists='append', index=False, chunksize=ETL_CONFIG['batch_size'])
            
            self.load_stats['fact_engagement'] = {
                'rows_loaded': len(df),
                'status': 'SUCCESS'
            }
            
            logger.info(f"✓ Loaded fact_engagement: {len(df)} rows")
            return len(df)
        except Exception as e:
            logger.error(f"✗ Error loading fact_engagement: {str(e)}")
            self.load_stats['fact_engagement'] = {'status': 'FAILED', 'error': str(e)}
            raise
    
    def load_all(self) -> int:
        """
        Load all transformed data into database.
        
        Returns:
            Total number of rows loaded
        """
        logger.info("Starting data loading...")
        logger.info("=" * 60)
        
        try:
            total_rows = 0
            
            total_rows += self.load_dim_student()
            total_rows += self.load_dim_course()
            total_rows += self.load_dim_assessment()
            total_rows += self.load_fact_assessment()
            total_rows += self.load_fact_learning_activity()
            total_rows += self.load_fact_engagement()
            
            logger.info("=" * 60)
            logger.info(f"✓ Data loading completed successfully")
            logger.info(f"  Total rows loaded: {total_rows:,}")
            
            return total_rows
        except Exception as e:
            logger.error(f"✗ Data loading failed: {str(e)}")
            raise
    
    def get_load_stats(self) -> Dict:
        """
        Get loading statistics.
        
        Returns:
            Dictionary of loading statistics
        """
        return self.load_stats
    
    def record_load_to_database(self, execution_stats: Dict):
        """
        Record load execution to database audit table.
        
        Args:
            execution_stats: Execution statistics dictionary
        """
        try:
            query = """
                INSERT INTO pipeline_execution_log 
                (pipeline_name, execution_status, start_time, end_time, 
                 total_rows_extracted, total_rows_cleaned, total_rows_loaded,
                 total_errors, total_warnings, execution_duration_seconds)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            start_time = execution_stats.get('start_time')
            end_time = execution_stats.get('end_time')
            duration = (end_time - start_time).total_seconds() if start_time and end_time else 0
            
            params = (
                execution_stats.get('pipeline_name'),
                execution_stats.get('status'),
                start_time,
                end_time,
                execution_stats.get('total_rows_extracted', 0),
                execution_stats.get('total_rows_cleaned', 0),
                execution_stats.get('total_rows_loaded', 0),
                len(execution_stats.get('errors', [])),
                len(execution_stats.get('warnings', [])),
                duration
            )
            
            self.db.execute_query(query, params)
            logger.info("Execution log recorded to database")
        except Exception as e:
            logger.error(f"Error recording execution log: {str(e)}")
    
    def close(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database engine connection closed")


if __name__ == "__main__":
    logger.info("Data Loader Module Loaded")
