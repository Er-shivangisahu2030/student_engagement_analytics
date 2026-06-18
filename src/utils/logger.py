"""
Logger Module
Centralized logging setup for the entire ETL pipeline.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from config import LOG_CONFIG


class PipelineLogger:
    """
    Centralized logger for the ETL pipeline.
    Handles both file and console logging.
    """
    
    _instance: Optional['PipelineLogger'] = None
    _loggers = {}
    
    def __new__(cls) -> 'PipelineLogger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the logger if not already initialized."""
        if not PipelineLogger._loggers:
            self._setup_loggers()
    
    @staticmethod
    def _setup_loggers() -> None:
        """Setup logging configuration."""
        # Ensure log directory exists
        log_file = LOG_CONFIG["log_file"]
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create formatter
        formatter = logging.Formatter(
            LOG_CONFIG["format"],
            datefmt=LOG_CONFIG["date_format"]
        )
        
        # File handler
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(getattr(logging, LOG_CONFIG["log_level"]))
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, LOG_CONFIG["log_level"]))
        console_handler.setFormatter(formatter)
        
        # Root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, LOG_CONFIG["log_level"]))
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Add handlers
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get or create a logger with the specified name.
        
        Args:
            name: Logger name (typically __name__)
        
        Returns:
            logging.Logger: Configured logger instance
        """
        return logging.getLogger(name)


class ETLExecutionLogger:
    """
    Specialized logger for tracking ETL pipeline execution metrics.
    """
    
    def __init__(self, pipeline_name: str):
        """
        Initialize ETL execution logger.
        
        Args:
            pipeline_name: Name of the ETL pipeline
        """
        self.pipeline_name = pipeline_name
        self.logger = PipelineLogger.get_logger(f"ETL.{pipeline_name}")
        self.execution_stats = {
            'pipeline_name': pipeline_name,
            'start_time': datetime.now(),
            'end_time': None,
            'status': 'RUNNING',
            'stages': {},
            'total_rows_extracted': 0,
            'total_rows_cleaned': 0,
            'total_rows_loaded': 0,
            'errors': [],
            'warnings': [],
        }
    
    def log_stage_start(self, stage_name: str) -> None:
        """
        Log the start of a pipeline stage.
        
        Args:
            stage_name: Name of the stage
        """
        self.execution_stats['stages'][stage_name] = {
            'start_time': datetime.now(),
            'status': 'RUNNING',
            'rows_processed': 0,
            'errors': []
        }
        self.logger.info(f"{'='*60}")
        self.logger.info(f"STAGE START: {stage_name}")
        self.logger.info(f"{'='*60}")
    
    def log_stage_end(self, stage_name: str, rows_processed: int = 0, status: str = "SUCCESS") -> None:
        """
        Log the completion of a pipeline stage.
        
        Args:
            stage_name: Name of the stage
            rows_processed: Number of rows processed
            status: Status of the stage (SUCCESS, FAILED, WARNING)
        """
        if stage_name in self.execution_stats['stages']:
            self.execution_stats['stages'][stage_name]['end_time'] = datetime.now()
            self.execution_stats['stages'][stage_name]['status'] = status
            self.execution_stats['stages'][stage_name]['rows_processed'] = rows_processed
            
            duration = (self.execution_stats['stages'][stage_name]['end_time'] - 
                       self.execution_stats['stages'][stage_name]['start_time']).total_seconds()
            
            self.logger.info(f"STAGE END: {stage_name} | Status: {status} | Rows: {rows_processed} | Duration: {duration:.2f}s")
            self.logger.info(f"{'='*60}")
    
    def log_extraction(self, file_name: str, rows_extracted: int) -> None:
        """
        Log data extraction metrics.
        
        Args:
            file_name: Name of the extracted file
            rows_extracted: Number of rows extracted
        """
        self.execution_stats['total_rows_extracted'] += rows_extracted
        self.logger.info(f"EXTRACT: {file_name} | Rows: {rows_extracted}")
    
    def log_cleaning(self, rows_before: int, rows_after: int, removed_rows: int) -> None:
        """
        Log data cleaning metrics.
        
        Args:
            rows_before: Rows before cleaning
            rows_after: Rows after cleaning
            removed_rows: Number of rows removed
        """
        self.execution_stats['total_rows_cleaned'] += removed_rows
        self.logger.info(f"CLEAN: Before={rows_before} | After={rows_after} | Removed={removed_rows}")
    
    def log_validation(self, file_name: str, valid: bool, issues: list = None) -> None:
        """
        Log data validation results.
        
        Args:
            file_name: Name of the validated file
            valid: Whether validation passed
            issues: List of validation issues
        """
        if valid:
            self.logger.info(f"VALIDATE: {file_name} | Status: PASSED ✓")
        else:
            self.logger.warning(f"VALIDATE: {file_name} | Status: FAILED ✗")
            if issues:
                for issue in issues:
                    self.logger.warning(f"  - {issue}")
                    self.execution_stats['warnings'].append(issue)
    
    def log_load(self, table_name: str, rows_loaded: int) -> None:
        """
        Log data loading metrics.
        
        Args:
            table_name: Name of the table
            rows_loaded: Number of rows loaded
        """
        self.execution_stats['total_rows_loaded'] += rows_loaded
        self.logger.info(f"LOAD: {table_name} | Rows: {rows_loaded}")
    
    def log_error(self, message: str, exception: Exception = None) -> None:
        """
        Log an error.
        
        Args:
            message: Error message
            exception: Exception object (optional)
        """
        self.logger.error(message)
        self.execution_stats['errors'].append(message)
        if exception:
            self.logger.error(f"Exception: {str(exception)}", exc_info=True)
    
    def log_warning(self, message: str) -> None:
        """
        Log a warning.
        
        Args:
            message: Warning message
        """
        self.logger.warning(message)
        self.execution_stats['warnings'].append(message)
    
    def log_info(self, message: str) -> None:
        """
        Log informational message.
        
        Args:
            message: Info message
        """
        self.logger.info(message)
    
    def finalize_execution(self, status: str = "SUCCESS") -> dict:
        """
        Finalize the execution and return statistics.
        
        Args:
            status: Final status of the pipeline
        
        Returns:
            dict: Execution statistics
        """
        self.execution_stats['end_time'] = datetime.now()
        self.execution_stats['status'] = status
        
        total_duration = (self.execution_stats['end_time'] - 
                         self.execution_stats['start_time']).total_seconds()
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"PIPELINE SUMMARY: {self.pipeline_name}")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Status: {status}")
        self.logger.info(f"Total Duration: {total_duration:.2f} seconds")
        self.logger.info(f"Total Rows Extracted: {self.execution_stats['total_rows_extracted']}")
        self.logger.info(f"Total Rows Cleaned: {self.execution_stats['total_rows_cleaned']}")
        self.logger.info(f"Total Rows Loaded: {self.execution_stats['total_rows_loaded']}")
        self.logger.info(f"Total Errors: {len(self.execution_stats['errors'])}")
        self.logger.info(f"Total Warnings: {len(self.execution_stats['warnings'])}")
        self.logger.info(f"{'='*60}\n")
        
        return self.execution_stats


# Create global logger instance
pipeline_logger = PipelineLogger()


if __name__ == "__main__":
    logger = PipelineLogger.get_logger(__name__)
    logger.info("Logger module initialized successfully")
