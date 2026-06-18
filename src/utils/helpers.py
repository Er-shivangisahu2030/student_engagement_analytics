"""
Helpers Module
Common utility functions for data processing and validation.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional
from datetime import datetime
import hashlib
import json

from config import FILE_CONFIG, REPORTS_PATH


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names to snake_case.
    
    Args:
        df: Input DataFrame
    
    Returns:
        DataFrame with normalized column names
    """
    df.columns = (df.columns
                  .str.strip()
                  .str.lower()
                  .str.replace(' ', '_', regex=False)
                  .str.replace('(', '', regex=False)
                  .str.replace(')', '', regex=False)
                  .str.replace('-', '_', regex=False))
    return df


def read_csv_safely(file_path: Path, **kwargs) -> pd.DataFrame:
    """
    Read CSV file with error handling.
    
    Args:
        file_path: Path to CSV file
        **kwargs: Additional arguments for pd.read_csv
    
    Returns:
        DataFrame
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is empty or invalid
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        df = pd.read_csv(file_path, encoding=FILE_CONFIG['encoding'], **kwargs)
        if df.empty:
            raise ValueError(f"File is empty: {file_path}")
        return df
    except pd.errors.ParserError as e:
        raise ValueError(f"Error parsing CSV file {file_path}: {str(e)}")


def save_csv_safely(df: pd.DataFrame, file_path: Path, index: bool = False) -> None:
    """
    Save DataFrame to CSV with error handling.
    
    Args:
        df: DataFrame to save
        file_path: Path to save file
        index: Whether to save index
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(file_path, index=index, encoding=FILE_CONFIG['encoding'])
    except Exception as e:
        raise IOError(f"Error saving CSV file {file_path}: {str(e)}")


def detect_and_fill_missing_values(df: pd.DataFrame, strategy: str = 'auto') -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Detect and handle missing values intelligently.
    
    Args:
        df: Input DataFrame
        strategy: Strategy for handling missing values ('auto', 'drop', 'fill')
    
    Returns:
        Tuple of (cleaned DataFrame, statistics)
    """
    stats = {
        'total_missing': int(df.isnull().sum().sum()),
        'columns_with_missing': {},
        'rows_dropped': 0,
        'values_filled': 0,
        'method': strategy
    }
    
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        if missing_count > 0:
            stats['columns_with_missing'][col] = int(missing_count)
            
            if strategy == 'auto':
                # Numeric columns: fill with mean
                if pd.api.types.is_numeric_dtype(df[col]):
                    fill_value = df[col].mean()
                    df[col].fillna(fill_value, inplace=True)
                    stats['values_filled'] += missing_count
                # Categorical columns: fill with mode
                else:
                    fill_value = df[col].mode()[0] if not df[col].mode().empty else 'Unknown'
                    df[col].fillna(fill_value, inplace=True)
                    stats['values_filled'] += missing_count
            elif strategy == 'drop':
                initial_rows = len(df)
                df = df.dropna(subset=[col])
                dropped = initial_rows - len(df)
                stats['rows_dropped'] += dropped
    
    return df, stats


def remove_duplicates(df: pd.DataFrame, subset: List[str] = None, keep: str = 'first') -> Tuple[pd.DataFrame, int]:
    """
    Remove duplicate rows.
    
    Args:
        df: Input DataFrame
        subset: Columns to consider for duplicates
        keep: Which duplicates to keep ('first', 'last', False)
    
    Returns:
        Tuple of (cleaned DataFrame, number of duplicates removed)
    """
    initial_count = len(df)
    df = df.drop_duplicates(subset=subset, keep=keep)
    duplicates_removed = initial_count - len(df)
    
    return df, duplicates_removed


def standardize_column_values(df: pd.DataFrame, column: str, mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Standardize values in a column using a mapping.
    
    Args:
        df: Input DataFrame
        column: Column to standardize
        mapping: Dictionary mapping old values to new values
    
    Returns:
        DataFrame with standardized values
    """
    df[column] = df[column].map(mapping).fillna(df[column])
    return df


def validate_data_types(df: pd.DataFrame, expected_types: Dict[str, type]) -> Tuple[bool, List[str]]:
    """
    Validate data types in DataFrame.
    
    Args:
        df: Input DataFrame
        expected_types: Dictionary of column names and expected types
    
    Returns:
        Tuple of (is_valid, list of errors)
    """
    errors = []
    
    for col, expected_type in expected_types.items():
        if col not in df.columns:
            errors.append(f"Column '{col}' not found in DataFrame")
            continue
        
        if expected_type == int:
            if not pd.api.types.is_numeric_dtype(df[col]):
                errors.append(f"Column '{col}' should be numeric but is {df[col].dtype}")
        elif expected_type == float:
            if not pd.api.types.is_float_dtype(df[col]):
                errors.append(f"Column '{col}' should be float but is {df[col].dtype}")
        elif expected_type == str:
            if not pd.api.types.is_object_dtype(df[col]):
                errors.append(f"Column '{col}' should be string but is {df[col].dtype}")
    
    return len(errors) == 0, errors


def calculate_missing_percentage(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate percentage of missing values per column.
    
    Args:
        df: Input DataFrame
    
    Returns:
        Dictionary of column names and missing percentages
    """
    return {col: (df[col].isnull().sum() / len(df)) * 100 for col in df.columns}


def generate_data_profile(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate a comprehensive data profile for a DataFrame.
    
    Args:
        df: Input DataFrame
    
    Returns:
        Dictionary containing data profile
    """
    profile = {
        'shape': {'rows': len(df), 'columns': len(df.columns)},
        'columns': list(df.columns),
        'data_types': df.dtypes.astype(str).to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'missing_percentage': calculate_missing_percentage(df),
        'duplicates': len(df[df.duplicated()]),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
        'numeric_summary': df.describe().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 0 else {},
    }
    
    return profile


def generate_validation_report(validation_results: Dict[str, Any], output_file: Optional[Path] = None) -> str:
    """
    Generate a validation report from validation results.
    
    Args:
        validation_results: Dictionary of validation results
        output_file: Optional path to save report
    
    Returns:
        Report as string
    """
    report = []
    report.append("=" * 80)
    report.append("DATA VALIDATION REPORT")
    report.append("=" * 80)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    for file_name, results in validation_results.items():
        report.append(f"\nFile: {file_name}")
        report.append("-" * 80)
        report.append(f"Status: {'✓ PASSED' if results['is_valid'] else '✗ FAILED'}")
        report.append(f"Rows: {results.get('total_rows', 'N/A')}")
        report.append(f"Columns: {results.get('total_columns', 'N/A')}")
        
        if results.get('issues'):
            report.append("\nIssues Found:")
            for issue in results['issues']:
                report.append(f"  - {issue}")
        
        if results.get('warnings'):
            report.append("\nWarnings:")
            for warning in results['warnings']:
                report.append(f"  ⚠ {warning}")
        
        report.append("")
    
    report.append("=" * 80)
    
    report_text = "\n".join(report)
    
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(report_text)
    
    return report_text


def generate_execution_report(execution_stats: Dict[str, Any], output_file: Optional[Path] = None) -> str:
    """
    Generate an execution report from pipeline execution statistics.
    
    Args:
        execution_stats: Execution statistics from ETLExecutionLogger
        output_file: Optional path to save report
    
    Returns:
        Report as string
    """
    report = []
    report.append("=" * 80)
    report.append("ETL PIPELINE EXECUTION REPORT")
    report.append("=" * 80)
    report.append(f"Pipeline: {execution_stats.get('pipeline_name', 'Unknown')}")
    report.append(f"Status: {execution_stats.get('status', 'Unknown')}")
    report.append(f"Start Time: {execution_stats.get('start_time', 'N/A')}")
    report.append(f"End Time: {execution_stats.get('end_time', 'N/A')}")
    report.append("")
    
    # Calculate duration
    if execution_stats.get('start_time') and execution_stats.get('end_time'):
        duration = (execution_stats['end_time'] - execution_stats['start_time']).total_seconds()
        report.append(f"Total Duration: {duration:.2f} seconds")
    
    report.append("")
    report.append("METRICS:")
    report.append("-" * 80)
    report.append(f"Total Rows Extracted: {execution_stats.get('total_rows_extracted', 0):,}")
    report.append(f"Total Rows Cleaned: {execution_stats.get('total_rows_cleaned', 0):,}")
    report.append(f"Total Rows Loaded: {execution_stats.get('total_rows_loaded', 0):,}")
    report.append(f"Total Errors: {len(execution_stats.get('errors', []))}")
    report.append(f"Total Warnings: {len(execution_stats.get('warnings', []))}")
    report.append("")
    
    # Stage details
    if execution_stats.get('stages'):
        report.append("STAGE DETAILS:")
        report.append("-" * 80)
        for stage_name, stage_info in execution_stats['stages'].items():
            report.append(f"\n{stage_name}:")
            report.append(f"  Status: {stage_info.get('status', 'Unknown')}")
            report.append(f"  Rows Processed: {stage_info.get('rows_processed', 0):,}")
            if stage_info.get('start_time') and stage_info.get('end_time'):
                stage_duration = (stage_info['end_time'] - stage_info['start_time']).total_seconds()
                report.append(f"  Duration: {stage_duration:.2f} seconds")
    
    # Errors
    if execution_stats.get('errors'):
        report.append("\n\nERRORS:")
        report.append("-" * 80)
        for i, error in enumerate(execution_stats['errors'], 1):
            report.append(f"{i}. {error}")
    
    # Warnings
    if execution_stats.get('warnings'):
        report.append("\n\nWARNINGS:")
        report.append("-" * 80)
        for i, warning in enumerate(execution_stats['warnings'], 1):
            report.append(f"{i}. {warning}")
    
    report.append("\n" + "=" * 80)
    
    report_text = "\n".join(report)
    
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(report_text)
    
    return report_text


def calculate_hash(data: str) -> str:
    """
    Calculate SHA256 hash of data.
    
    Args:
        data: Input string
    
    Returns:
        SHA256 hash
    """
    return hashlib.sha256(data.encode()).hexdigest()


def chunk_dataframe(df: pd.DataFrame, chunk_size: int = 1000) -> List[pd.DataFrame]:
    """
    Split DataFrame into chunks.
    
    Args:
        df: Input DataFrame
        chunk_size: Size of each chunk
    
    Returns:
        List of DataFrame chunks
    """
    chunks = []
    for i in range(0, len(df), chunk_size):
        chunks.append(df.iloc[i:i + chunk_size].copy())
    return chunks


if __name__ == "__main__":
    print("Helpers module loaded successfully")
