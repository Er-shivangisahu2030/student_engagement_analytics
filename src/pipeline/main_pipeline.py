"""
Main ETL Pipeline Module
Orchestrates the complete ETL workflow.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import PROJECT_ROOT
from database.connection import db_connection
from database.schema import SchemaGenerator
from etl.extract import DataExtractor
from etl.data_cleaning import DataCleaner
from etl.data_validation import DataValidator
from etl.data_transform import DataTransformer
from etl.data_load import DataLoader
from utils.logger import ETLExecutionLogger
from utils.helpers import save_csv_safely, generate_execution_report


# Setup logging
logger = logging.getLogger(__name__)


class StudentEngagementPipeline:
    """
    Complete ETL pipeline for Student Engagement & Learning Streak Analytics.
    """
    
    def __init__(self):
        """Initialize the pipeline."""
        self.pipeline_name = "Student Engagement & Learning Streak Analytics"
        self.execution_logger = ETLExecutionLogger(self.pipeline_name)
        self.stats = {
            'extracted_data': None,
            'cleaned_data': None,
            'validation_results': None,
            'transformed_data': None,
            'load_stats': None,
        }
    
    def extract(self) -> bool:
        """
        Execute extraction stage.
        
        Returns:
            bool: True if successful
        """
        self.execution_logger.log_stage_start("EXTRACT")
        
        try:
            extractor = DataExtractor()
            self.stats['extracted_data'] = extractor.extract_all()
            
            # Log extraction metrics
            stats = extractor.get_extraction_stats()
            total_rows = sum(s['rows'] for s in stats.values())
            
            for table_name, table_stats in stats.items():
                self.execution_logger.log_extraction(table_name, table_stats['rows'])
            
            self.execution_logger.log_stage_end("EXTRACT", total_rows, "SUCCESS")
            return True
        except Exception as e:
            self.execution_logger.log_error(f"Extraction failed: {str(e)}", e)
            self.execution_logger.log_stage_end("EXTRACT", 0, "FAILED")
            return False
    
    def clean(self) -> bool:
        """
        Execute cleaning stage.
        
        Returns:
            bool: True if successful
        """
        self.execution_logger.log_stage_start("CLEAN")
        
        try:
            cleaner = DataCleaner(self.stats['extracted_data'])
            self.stats['cleaned_data'] = cleaner.clean_all()
            
            # Log cleaning metrics
            stats = cleaner.get_cleaning_stats()
            for table_name, table_stats in stats.items():
                self.execution_logger.log_cleaning(
                    table_stats['initial_rows'],
                    table_stats['final_rows'],
                    table_stats['rows_removed']
                )
            
            total_rows = sum(s['final_rows'] for s in stats.values())
            self.execution_logger.log_stage_end("CLEAN", total_rows, "SUCCESS")
            return True
        except Exception as e:
            self.execution_logger.log_error(f"Cleaning failed: {str(e)}", e)
            self.execution_logger.log_stage_end("CLEAN", 0, "FAILED")
            return False
    
    def validate(self) -> bool:
        """
        Execute validation stage.
        
        Returns:
            bool: True if validation passed
        """
        self.execution_logger.log_stage_start("VALIDATE")
        
        try:
            validator = DataValidator(self.stats['cleaned_data'])
            validation_passed = validator.validate_all()
            self.stats['validation_results'] = validator.get_validation_results()
            
            # Log validation results
            quality_scores = validator.get_quality_scores()
            for table_name, score in quality_scores.items():
                results = self.stats['validation_results'][table_name]
                self.execution_logger.log_validation(
                    table_name,
                    results['is_valid'],
                    results['issues'] + results['warnings']
                )
            
            self.execution_logger.log_stage_end("VALIDATE", 0, "SUCCESS")
            return validation_passed
        except Exception as e:
            self.execution_logger.log_error(f"Validation failed: {str(e)}", e)
            self.execution_logger.log_stage_end("VALIDATE", 0, "FAILED")
            return False
    
    def transform(self) -> bool:
        """
        Execute transformation stage.
        
        Returns:
            bool: True if successful
        """
        self.execution_logger.log_stage_start("TRANSFORM")
        
        try:
            transformer = DataTransformer(self.stats['cleaned_data'])
            self.stats['transformed_data'] = transformer.transform_all()
            
            # Log transformation metrics
            total_rows = sum(len(df) for df in self.stats['transformed_data'].values())
            self.execution_logger.log_stage_end("TRANSFORM", total_rows, "SUCCESS")
            
            # Save transformed data to CSV for backup
            self._save_transformed_data()
            return True
        except Exception as e:
            self.execution_logger.log_error(f"Transformation failed: {str(e)}", e)
            self.execution_logger.log_stage_end("TRANSFORM", 0, "FAILED")
            return False
    
    def load(self) -> bool:
        """
        Execute loading stage.
        
        Returns:
            bool: True if successful
        """
        self.execution_logger.log_stage_start("LOAD")
        
        try:
            # Create database schema first
            logger.info("Creating database schema...")
            SchemaGenerator.create_schema(db_connection)
            SchemaGenerator.create_views(db_connection)
            
            # Load data
            loader = DataLoader(self.stats['transformed_data'])
            total_rows = loader.load_all()
            self.stats['load_stats'] = loader.get_load_stats()
            
            # Log loading metrics
            for table_name, stats in self.stats['load_stats'].items():
                if stats['status'] == 'SUCCESS':
                    self.execution_logger.log_load(table_name, stats['rows_loaded'])
            
            # Record execution to database
            execution_stats = self.execution_logger.execution_stats
            loader.record_load_to_database(execution_stats)
            loader.close()
            
            self.execution_logger.log_stage_end("LOAD", total_rows, "SUCCESS")
            return True
        except Exception as e:
            self.execution_logger.log_error(f"Loading failed: {str(e)}", e)
            self.execution_logger.log_stage_end("LOAD", 0, "FAILED")
            return False
    
    def run(self) -> bool:
        """
        Execute complete ETL pipeline.
        
        Returns:
            bool: True if all stages successful
        """
        logger.info("=" * 80)
        logger.info(f"Starting ETL Pipeline: {self.pipeline_name}")
        logger.info("=" * 80)
        
        try:
            # Test database connection
            if not db_connection.test_connection():
                self.execution_logger.log_error("Database connection failed")
                return False
            
            # Execute pipeline stages
            if not self.extract():
                return False
            
            if not self.clean():
                return False
            
            if not self.validate():
                self.execution_logger.log_warning("Validation warnings detected but continuing...")
            
            if not self.transform():
                return False
            
            if not self.load():
                return False
            
            # Finalize execution
            execution_stats = self.execution_logger.finalize_execution("SUCCESS")
            
            # Generate final report
            self._generate_final_report(execution_stats)
            
            logger.info("=" * 80)
            logger.info(f"✓ ETL Pipeline completed successfully!")
            logger.info("=" * 80)
            
            return True
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
            self.execution_logger.finalize_execution("FAILED")
            return False
    
    def _save_transformed_data(self):
        """Save transformed data to CSV files for backup."""
        logger.info("Saving transformed data to CSV...")
        
        try:
            output_path = PROJECT_ROOT / "data" / "processed"
            output_path.mkdir(parents=True, exist_ok=True)
            
            for table_name, df in self.stats['transformed_data'].items():
                file_path = output_path / f"{table_name}.csv"
                save_csv_safely(df, file_path)
                logger.info(f"  ✓ Saved {table_name}: {len(df)} rows")
        except Exception as e:
            logger.error(f"Error saving transformed data: {str(e)}")
    
    def _generate_final_report(self, execution_stats: dict):
        """Generate final execution report."""
        try:
            report_file = PROJECT_ROOT / "data" / "reports" / "etl_execution_report.txt"
            report = generate_execution_report(execution_stats, report_file)
            logger.info(f"Execution report saved to: {report_file}")
        except Exception as e:
            logger.error(f"Error generating final report: {str(e)}")


def main():
    """Main entry point for the ETL pipeline."""
    pipeline = StudentEngagementPipeline()
    success = pipeline.run()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
