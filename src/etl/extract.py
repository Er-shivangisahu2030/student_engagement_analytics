"""
Data Extraction Module
Handles extraction of raw data from various sources.
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Optional

from config import ETL_CONFIG
from utils.helpers import read_csv_safely, normalize_column_names


logger = logging.getLogger(__name__)


class DataExtractor:
    """
    Extracts raw data from CSV files.
    """
    
    def __init__(self, input_path: Optional[Path] = None):
        """
        Initialize the extractor.
        
        Args:
            input_path: Optional path to input directory
        """
        self.input_path = input_path or ETL_CONFIG['input_files']
        self.extracted_data: Dict[str, pd.DataFrame] = {}
        self.extraction_stats = {}
    
    def extract_assessments(self) -> pd.DataFrame:
        """
        Extract assessments data.
        
        Returns:
            DataFrame with assessments data
        """
        logger.info("Extracting assessments data...")
        try:
            file_path = self.input_path.get('assessments') if isinstance(self.input_path, dict) else Path(self.input_path) / 'assessments.csv'
            df = read_csv_safely(file_path)
            df = normalize_column_names(df)
            
            self.extracted_data['assessments'] = df
            self.extraction_stats['assessments'] = {
                'rows': len(df),
                'columns': len(df.columns),
                'file_path': str(file_path)
            }
            
            logger.info(f"✓ Extracted assessments: {len(df)} rows, {len(df.columns)} columns")
            return df
        except Exception as e:
            logger.error(f"✗ Error extracting assessments: {str(e)}")
            raise
    
    def extract_students(self) -> pd.DataFrame:
        """
        Extract student information data.
        
        Returns:
            DataFrame with student data
        """
        logger.info("Extracting student information...")
        try:
            file_path = self.input_path.get('students') if isinstance(self.input_path, dict) else Path(self.input_path) / 'studentInfo.csv'
            df = read_csv_safely(file_path)
            df = normalize_column_names(df)
            
            self.extracted_data['students'] = df
            self.extraction_stats['students'] = {
                'rows': len(df),
                'columns': len(df.columns),
                'file_path': str(file_path)
            }
            
            logger.info(f"✓ Extracted students: {len(df)} rows, {len(df.columns)} columns")
            return df
        except Exception as e:
            logger.error(f"✗ Error extracting students: {str(e)}")
            raise
    
    def extract_registrations(self) -> pd.DataFrame:
        """
        Extract student registration data.
        
        Returns:
            DataFrame with registration data
        """
        logger.info("Extracting student registrations...")
        try:
            file_path = self.input_path.get('registrations') if isinstance(self.input_path, dict) else Path(self.input_path) / 'studentRegistration.csv'
            df = read_csv_safely(file_path)
            df = normalize_column_names(df)
            
            self.extracted_data['registrations'] = df
            self.extraction_stats['registrations'] = {
                'rows': len(df),
                'columns': len(df.columns),
                'file_path': str(file_path)
            }
            
            logger.info(f"✓ Extracted registrations: {len(df)} rows, {len(df.columns)} columns")
            return df
        except Exception as e:
            logger.error(f"✗ Error extracting registrations: {str(e)}")
            raise
    
    def extract_assessment_results(self) -> pd.DataFrame:
        """
        Extract student assessment results.
        
        Returns:
            DataFrame with assessment results
        """
        logger.info("Extracting student assessment results...")
        try:
            file_path = self.input_path.get('assessment_results') if isinstance(self.input_path, dict) else Path(self.input_path) / 'studentAssessment.csv'
            df = read_csv_safely(file_path)
            df = normalize_column_names(df)
            
            self.extracted_data['assessment_results'] = df
            self.extraction_stats['assessment_results'] = {
                'rows': len(df),
                'columns': len(df.columns),
                'file_path': str(file_path)
            }
            
            logger.info(f"✓ Extracted assessment results: {len(df)} rows, {len(df.columns)} columns")
            return df
        except Exception as e:
            logger.error(f"✗ Error extracting assessment results: {str(e)}")
            raise
    
    def extract_activity(self) -> pd.DataFrame:
        """
        Extract student activity (clicks) data.
        
        Returns:
            DataFrame with activity data
        """
        logger.info("Extracting student activity data...")
        try:
            file_path = self.input_path.get('activity') if isinstance(self.input_path, dict) else Path(self.input_path) / 'studentActivity.csv'
            df = read_csv_safely(file_path)
            df = normalize_column_names(df)
            
            self.extracted_data['activity'] = df
            self.extraction_stats['activity'] = {
                'rows': len(df),
                'columns': len(df.columns),
                'file_path': str(file_path)
            }
            
            logger.info(f"✓ Extracted activity: {len(df)} rows, {len(df.columns)} columns")
            return df
        except Exception as e:
            logger.error(f"✗ Error extracting activity: {str(e)}")
            raise
    
    def extract_all(self) -> Dict[str, pd.DataFrame]:
        """
        Extract all data sources.
        
        Returns:
            Dictionary of all extracted DataFrames
        """
        logger.info("Starting data extraction...")
        logger.info("=" * 60)
        
        try:
            self.extract_assessments()
            self.extract_students()
            self.extract_registrations()
            self.extract_assessment_results()
            self.extract_activity()
            
            logger.info("=" * 60)
            logger.info(f"✓ Data extraction completed successfully")
            logger.info(f"  Total files extracted: {len(self.extracted_data)}")
            logger.info(f"  Total rows extracted: {sum(stats['rows'] for stats in self.extraction_stats.values())}")
            
            return self.extracted_data
        except Exception as e:
            logger.error(f"✗ Data extraction failed: {str(e)}")
            raise
    
    def get_extraction_stats(self) -> Dict:
        """
        Get extraction statistics.
        
        Returns:
            Dictionary of extraction statistics
        """
        return self.extraction_stats
    
    def get_extracted_data(self, table_name: str) -> Optional[pd.DataFrame]:
        """
        Get extracted data for a specific table.
        
        Args:
            table_name: Name of the table
        
        Returns:
            DataFrame or None if not found
        """
        return self.extracted_data.get(table_name)


if __name__ == "__main__":
    extractor = DataExtractor()
    data = extractor.extract_all()
    print(f"Extracted {len(data)} tables")
    for table_name, df in data.items():
        print(f"  - {table_name}: {len(df)} rows, {len(df.columns)} columns")
