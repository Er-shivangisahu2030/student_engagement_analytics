"""
Data Cleaning Module
Handles cleaning and preprocessing of raw data.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple

from utils.helpers import (
    detect_and_fill_missing_values,
    remove_duplicates,
    standardize_column_values
)
from config import VALID_REGIONS, VALID_EDUCATION_LEVELS, VALID_FINAL_RESULTS


logger = logging.getLogger(__name__)


class DataCleaner:
    """
    Cleans and preprocesses extracted data.
    """
    
    def __init__(self, data: Dict[str, pd.DataFrame]):
        """
        Initialize the cleaner with extracted data.
        
        Args:
            data: Dictionary of extracted DataFrames
        """
        self.raw_data = data
        self.cleaned_data: Dict[str, pd.DataFrame] = {}
        self.cleaning_stats = {}
    
    def clean_assessments(self) -> pd.DataFrame:
        """
        Clean assessments data.
        
        Returns:
            Cleaned DataFrame
        """
        logger.info("Cleaning assessments data...")
        df = self.raw_data['assessments'].copy()
        
        initial_rows = len(df)
        stats = {'initial_rows': initial_rows}
        
        try:
            # Remove rows where code_module is null
            df = df.dropna(subset=['code_module'])
            stats['rows_after_null_drop'] = len(df)
            
            # Remove duplicates
            df, duplicates_removed = remove_duplicates(df, subset=['id_assessment'])
            stats['duplicates_removed'] = duplicates_removed
            
            # Fill missing values in date (use 0 for exam dates)
            df['date'] = df['date'].fillna(0).astype(int)
            
            # Ensure weight is numeric
            df['weight'] = pd.to_numeric(df['weight'], errors='coerce').fillna(0)
            
            # Remove rows with invalid assessment types
            df = df[df['assessment_type'].isin(['TMA', 'Exam', 'CMA'])]
            stats['rows_after_type_filter'] = len(df)
            
            final_rows = len(df)
            stats['final_rows'] = final_rows
            stats['rows_removed'] = initial_rows - final_rows
            
            self.cleaned_data['assessments'] = df
            self.cleaning_stats['assessments'] = stats
            
            logger.info(f"✓ Cleaned assessments: {initial_rows} → {final_rows} rows")
            logger.info(f"  Duplicates removed: {duplicates_removed}")
            
            return df
        except Exception as e:
            logger.error(f"✗ Error cleaning assessments: {str(e)}")
            raise
    
    def clean_students(self) -> pd.DataFrame:
        """
        Clean student data.
        
        Returns:
            Cleaned DataFrame
        """
        logger.info("Cleaning student data...")
        df = self.raw_data['students'].copy()
        
        initial_rows = len(df)
        stats = {'initial_rows': initial_rows}
        
        try:
            # Remove duplicates
            df, duplicates_removed = remove_duplicates(df, subset=['id_student'])
            stats['duplicates_removed'] = duplicates_removed
            
            # Handle missing values
            df['gender'] = df['gender'].fillna('Unknown')
            df['region'] = df['region'].fillna('Unknown')
            df['highest_education'] = df['highest_education'].fillna('Unknown')
            df['imd_band'] = df['imd_band'].fillna('Unknown')
            df['age_band'] = df['age_band'].fillna('Unknown')
            
            # Standardize region names
            valid_regions = VALID_REGIONS
            df.loc[~df['region'].isin(valid_regions), 'region'] = 'Other'
            
            # Standardize education levels
            valid_education = VALID_EDUCATION_LEVELS
            df.loc[~df['highest_education'].isin(valid_education), 'highest_education'] = 'Unknown'
            
            # Add enrollment year (extract from index or set to current)
            df['enrollment_year'] = 2013
            
            final_rows = len(df)
            stats['final_rows'] = final_rows
            stats['rows_removed'] = initial_rows - final_rows
            
            self.cleaned_data['students'] = df
            self.cleaning_stats['students'] = stats
            
            logger.info(f"✓ Cleaned students: {initial_rows} → {final_rows} rows")
            logger.info(f"  Duplicates removed: {duplicates_removed}")
            
            return df
        except Exception as e:
            logger.error(f"✗ Error cleaning students: {str(e)}")
            raise
    
    def clean_registrations(self) -> pd.DataFrame:
        """
        Clean student registration data.
        
        Returns:
            Cleaned DataFrame
        """
        logger.info("Cleaning registration data...")
        df = self.raw_data['registrations'].copy()
        
        initial_rows = len(df)
        stats = {'initial_rows': initial_rows}
        
        try:
            # Remove duplicates
            df, duplicates_removed = remove_duplicates(df, subset=['id_registration'])
            stats['duplicates_removed'] = duplicates_removed
            
            # Remove rows with missing critical fields
            df = df.dropna(subset=['id_student', 'code_module', 'code_presentation'])
            stats['rows_after_null_drop'] = len(df)
            
            # Standardize final result
            valid_results = VALID_FINAL_RESULTS
            df['final_result'] = df['final_result'].apply(
                lambda x: x if pd.notna(x) and x in valid_results else 'Unknown'
            )
            
            # Fill missing date values
            df['date_registration'] = df['date_registration'].fillna(-10)
            df['date_unregistration'] = df['date_unregistration'].fillna(np.nan)
            
            final_rows = len(df)
            stats['final_rows'] = final_rows
            stats['rows_removed'] = initial_rows - final_rows
            
            self.cleaned_data['registrations'] = df
            self.cleaning_stats['registrations'] = stats
            
            logger.info(f"✓ Cleaned registrations: {initial_rows} → {final_rows} rows")
            logger.info(f"  Duplicates removed: {duplicates_removed}")
            
            return df
        except Exception as e:
            logger.error(f"✗ Error cleaning registrations: {str(e)}")
            raise
    
    def clean_assessment_results(self) -> pd.DataFrame:
        """
        Clean student assessment results.
        
        Returns:
            Cleaned DataFrame
        """
        logger.info("Cleaning assessment results...")
        df = self.raw_data['assessment_results'].copy()
        
        initial_rows = len(df)
        stats = {'initial_rows': initial_rows}
        
        try:
            # Remove duplicates
            df, duplicates_removed = remove_duplicates(df, subset=['id_student_assessment'])
            stats['duplicates_removed'] = duplicates_removed
            
            # Remove rows with missing critical fields
            df = df.dropna(subset=['id_student', 'id_assessment'])
            stats['rows_after_null_drop'] = len(df)
            
            # Ensure score is numeric and in valid range
            df['score'] = pd.to_numeric(df['score'], errors='coerce')
            df = df.dropna(subset=['score'])
            df.loc[df['score'] < 0, 'score'] = 0
            df.loc[df['score'] > 100, 'score'] = 100
            
            # Handle is_banked column
            if 'is_banked' in df.columns:
                df['is_banked'] = df['is_banked'].fillna(0).astype(int)
            
            final_rows = len(df)
            stats['final_rows'] = final_rows
            stats['rows_removed'] = initial_rows - final_rows
            
            self.cleaned_data['assessment_results'] = df
            self.cleaning_stats['assessment_results'] = stats
            
            logger.info(f"✓ Cleaned assessment results: {initial_rows} → {final_rows} rows")
            logger.info(f"  Duplicates removed: {duplicates_removed}")
            
            return df
        except Exception as e:
            logger.error(f"✗ Error cleaning assessment results: {str(e)}")
            raise
    
    def clean_activity(self) -> pd.DataFrame:
        """
        Clean student activity data.
        
        Returns:
            Cleaned DataFrame
        """
        logger.info("Cleaning activity data...")
        df = self.raw_data['activity'].copy()
        
        initial_rows = len(df)
        stats = {'initial_rows': initial_rows}
        
        try:
            # Remove duplicates
            df, duplicates_removed = remove_duplicates(df, subset=['id_student_activity'])
            stats['duplicates_removed'] = duplicates_removed
            
            # Remove rows with missing critical fields
            df = df.dropna(subset=['id_student', 'code_module'])
            stats['rows_after_null_drop'] = len(df)
            
            # Ensure numeric fields are numeric
            df['date'] = pd.to_numeric(df['date'], errors='coerce').fillna(0).astype(int)
            df['sum_click'] = pd.to_numeric(df['sum_click'], errors='coerce').fillna(0).astype(int)
            
            # Remove rows with negative clicks
            df = df[df['sum_click'] >= 0]
            stats['rows_after_validation'] = len(df)
            
            # Fill missing activity_type
            if 'activity_type' in df.columns:
                df['activity_type'] = df['activity_type'].fillna('Unknown')
            
            final_rows = len(df)
            stats['final_rows'] = final_rows
            stats['rows_removed'] = initial_rows - final_rows
            
            self.cleaned_data['activity'] = df
            self.cleaning_stats['activity'] = stats
            
            logger.info(f"✓ Cleaned activity: {initial_rows} → {final_rows} rows")
            logger.info(f"  Duplicates removed: {duplicates_removed}")
            
            return df
        except Exception as e:
            logger.error(f"✗ Error cleaning activity: {str(e)}")
            raise
    
    def clean_all(self) -> Dict[str, pd.DataFrame]:
        """
        Clean all data.
        
        Returns:
            Dictionary of cleaned DataFrames
        """
        logger.info("Starting data cleaning...")
        logger.info("=" * 60)
        
        try:
            self.clean_assessments()
            self.clean_students()
            self.clean_registrations()
            self.clean_assessment_results()
            self.clean_activity()
            
            # Calculate summary statistics
            total_rows_before = sum(stats['initial_rows'] for stats in self.cleaning_stats.values())
            total_rows_after = sum(stats['final_rows'] for stats in self.cleaning_stats.values())
            total_rows_removed = total_rows_before - total_rows_after
            
            logger.info("=" * 60)
            logger.info(f"✓ Data cleaning completed successfully")
            logger.info(f"  Total rows before: {total_rows_before:,}")
            logger.info(f"  Total rows after: {total_rows_after:,}")
            logger.info(f"  Total rows removed: {total_rows_removed:,}")
            
            return self.cleaned_data
        except Exception as e:
            logger.error(f"✗ Data cleaning failed: {str(e)}")
            raise
    
    def get_cleaning_stats(self) -> Dict:
        """
        Get cleaning statistics.
        
        Returns:
            Dictionary of cleaning statistics
        """
        return self.cleaning_stats
    
    def get_cleaned_data(self, table_name: str) -> pd.DataFrame:
        """
        Get cleaned data for a specific table.
        
        Args:
            table_name: Name of the table
        
        Returns:
            Cleaned DataFrame
        """
        return self.cleaned_data.get(table_name)


if __name__ == "__main__":
    logger.info("Data Cleaner Module Loaded")
