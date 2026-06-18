"""
Data Validation Module
Performs comprehensive data quality validation.
"""

import pandas as pd
import logging
from typing import Dict, List, Tuple

from utils.helpers import (
    validate_data_types,
    calculate_missing_percentage,
    generate_data_profile,
    generate_validation_report
)
from config import VALIDATION_RULES, ETL_CONFIG, REPORTS_PATH


logger = logging.getLogger(__name__)


class DataValidator:
    """
    Validates data quality and completeness.
    """
    
    def __init__(self, data: Dict[str, pd.DataFrame]):
        """
        Initialize the validator with data.
        
        Args:
            data: Dictionary of DataFrames to validate
        """
        self.data = data
        self.validation_results = {}
        self.quality_scores = {}
    
    def validate_assessments(self) -> Tuple[bool, List[str], float]:
        """
        Validate assessments data.
        
        Returns:
            Tuple of (is_valid, issues, quality_score)
        """
        logger.info("Validating assessments data...")
        df = self.data['assessments']
        issues = []
        warnings = []
        
        try:
            # Check required columns
            required_cols = VALIDATION_RULES['assessments']['required_columns']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                issues.append(f"Missing required columns: {missing_cols}")
            
            # Check minimum rows
            if len(df) < ETL_CONFIG['quality_thresholds']['min_rows']:
                issues.append(f"Insufficient rows: {len(df)} < {ETL_CONFIG['quality_thresholds']['min_rows']}")
            
            # Check for missing values
            missing_pct = calculate_missing_percentage(df)
            max_missing = ETL_CONFIG['quality_thresholds']['max_missing_percentage']
            for col, pct in missing_pct.items():
                if pct > max_missing:
                    warnings.append(f"Column '{col}' has {pct:.2f}% missing values")
            
            # Check data types
            valid, type_errors = validate_data_types(df, VALIDATION_RULES['assessments']['data_types'])
            if not valid:
                warnings.extend(type_errors)
            
            # Validate assessment type values
            valid_types = ['TMA', 'Exam', 'CMA']
            invalid_types = df[~df['assessment_type'].isin(valid_types)]['assessment_type'].unique()
            if len(invalid_types) > 0:
                warnings.append(f"Invalid assessment types found: {invalid_types}")
            
            # Calculate quality score (0-100)
            quality_score = 100
            quality_score -= len(issues) * 20
            quality_score -= len(warnings) * 5
            quality_score = max(0, quality_score)
            
            is_valid = len(issues) == 0
            
            self.validation_results['assessments'] = {
                'is_valid': is_valid,
                'issues': issues,
                'warnings': warnings,
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'missing_values': int(df.isnull().sum().sum()),
                'duplicate_rows': len(df[df.duplicated()]),
                'quality_score': quality_score
            }
            self.quality_scores['assessments'] = quality_score
            
            logger.info(f"✓ Assessments validation: {'PASSED' if is_valid else 'FAILED'} (Score: {quality_score:.1f}%)")
            return is_valid, issues + warnings, quality_score
        except Exception as e:
            logger.error(f"✗ Error validating assessments: {str(e)}")
            return False, [str(e)], 0
    
    def validate_students(self) -> Tuple[bool, List[str], float]:
        """
        Validate student data.
        
        Returns:
            Tuple of (is_valid, issues, quality_score)
        """
        logger.info("Validating student data...")
        df = self.data['students']
        issues = []
        warnings = []
        
        try:
            # Check required columns
            required_cols = VALIDATION_RULES['studentInfo']['required_columns']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                issues.append(f"Missing required columns: {missing_cols}")
            
            # Check minimum rows
            if len(df) < ETL_CONFIG['quality_thresholds']['min_rows']:
                issues.append(f"Insufficient rows: {len(df)}")
            
            # Check for missing values
            missing_pct = calculate_missing_percentage(df)
            max_missing = ETL_CONFIG['quality_thresholds']['max_missing_percentage']
            for col, pct in missing_pct.items():
                if pct > max_missing:
                    warnings.append(f"Column '{col}' has {pct:.2f}% missing values")
            
            # Check for duplicates
            duplicates = len(df[df.duplicated(subset=['id_student'])])
            if duplicates > 0:
                warnings.append(f"Found {duplicates} duplicate students")
            
            # Validate data types
            valid, type_errors = validate_data_types(df, VALIDATION_RULES['studentInfo']['data_types'])
            if not valid:
                warnings.extend(type_errors)
            
            # Calculate quality score
            quality_score = 100
            quality_score -= len(issues) * 20
            quality_score -= len(warnings) * 5
            quality_score = max(0, quality_score)
            
            is_valid = len(issues) == 0
            
            self.validation_results['students'] = {
                'is_valid': is_valid,
                'issues': issues,
                'warnings': warnings,
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'missing_values': int(df.isnull().sum().sum()),
                'duplicate_rows': len(df[df.duplicated()]),
                'quality_score': quality_score
            }
            self.quality_scores['students'] = quality_score
            
            logger.info(f"✓ Students validation: {'PASSED' if is_valid else 'FAILED'} (Score: {quality_score:.1f}%)")
            return is_valid, issues + warnings, quality_score
        except Exception as e:
            logger.error(f"✗ Error validating students: {str(e)}")
            return False, [str(e)], 0
    
    def validate_registrations(self) -> Tuple[bool, List[str], float]:
        """
        Validate registration data.
        
        Returns:
            Tuple of (is_valid, issues, quality_score)
        """
        logger.info("Validating registration data...")
        df = self.data['registrations']
        issues = []
        warnings = []
        
        try:
            # Check required columns
            required_cols = VALIDATION_RULES['studentRegistration']['required_columns']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                issues.append(f"Missing required columns: {missing_cols}")
            
            # Check minimum rows
            if len(df) < ETL_CONFIG['quality_thresholds']['min_rows']:
                issues.append(f"Insufficient rows: {len(df)}")
            
            # Check for missing values
            missing_pct = calculate_missing_percentage(df)
            for col, pct in missing_pct.items():
                if pct > 30:
                    warnings.append(f"Column '{col}' has {pct:.2f}% missing values")
            
            # Calculate quality score
            quality_score = 100
            quality_score -= len(issues) * 20
            quality_score -= len(warnings) * 5
            quality_score = max(0, quality_score)
            
            is_valid = len(issues) == 0
            
            self.validation_results['registrations'] = {
                'is_valid': is_valid,
                'issues': issues,
                'warnings': warnings,
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'missing_values': int(df.isnull().sum().sum()),
                'duplicate_rows': len(df[df.duplicated()]),
                'quality_score': quality_score
            }
            self.quality_scores['registrations'] = quality_score
            
            logger.info(f"✓ Registrations validation: {'PASSED' if is_valid else 'FAILED'} (Score: {quality_score:.1f}%)")
            return is_valid, issues + warnings, quality_score
        except Exception as e:
            logger.error(f"✗ Error validating registrations: {str(e)}")
            return False, [str(e)], 0
    
    def validate_assessment_results(self) -> Tuple[bool, List[str], float]:
        """
        Validate assessment results.
        
        Returns:
            Tuple of (is_valid, issues, quality_score)
        """
        logger.info("Validating assessment results...")
        df = self.data['assessment_results']
        issues = []
        warnings = []
        
        try:
            # Check required columns
            required_cols = VALIDATION_RULES['studentAssessment']['required_columns']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                issues.append(f"Missing required columns: {missing_cols}")
            
            # Check minimum rows
            if len(df) < ETL_CONFIG['quality_thresholds']['min_rows']:
                issues.append(f"Insufficient rows: {len(df)}")
            
            # Check score range
            if 'score' in df.columns:
                invalid_scores = df[(df['score'] < 0) | (df['score'] > 100)]
                if len(invalid_scores) > 0:
                    warnings.append(f"Found {len(invalid_scores)} scores outside 0-100 range")
            
            # Check for missing values
            missing_pct = calculate_missing_percentage(df)
            for col, pct in missing_pct.items():
                if pct > 30:
                    warnings.append(f"Column '{col}' has {pct:.2f}% missing values")
            
            # Calculate quality score
            quality_score = 100
            quality_score -= len(issues) * 20
            quality_score -= len(warnings) * 5
            quality_score = max(0, quality_score)
            
            is_valid = len(issues) == 0
            
            self.validation_results['assessment_results'] = {
                'is_valid': is_valid,
                'issues': issues,
                'warnings': warnings,
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'missing_values': int(df.isnull().sum().sum()),
                'duplicate_rows': len(df[df.duplicated()]),
                'quality_score': quality_score
            }
            self.quality_scores['assessment_results'] = quality_score
            
            logger.info(f"✓ Assessment results validation: {'PASSED' if is_valid else 'FAILED'} (Score: {quality_score:.1f}%)")
            return is_valid, issues + warnings, quality_score
        except Exception as e:
            logger.error(f"✗ Error validating assessment results: {str(e)}")
            return False, [str(e)], 0
    
    def validate_activity(self) -> Tuple[bool, List[str], float]:
        """
        Validate activity data.
        
        Returns:
            Tuple of (is_valid, issues, quality_score)
        """
        logger.info("Validating activity data...")
        df = self.data['activity']
        issues = []
        warnings = []
        
        try:
            # Check required columns
            required_cols = VALIDATION_RULES['studentActivity']['required_columns']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                issues.append(f"Missing required columns: {missing_cols}")
            
            # Check for missing values
            missing_pct = calculate_missing_percentage(df)
            for col, pct in missing_pct.items():
                if pct > 30:
                    warnings.append(f"Column '{col}' has {pct:.2f}% missing values")
            
            # Validate click counts
            if 'sum_click' in df.columns:
                negative_clicks = len(df[df['sum_click'] < 0])
                if negative_clicks > 0:
                    warnings.append(f"Found {negative_clicks} negative click counts")
            
            # Calculate quality score
            quality_score = 100
            quality_score -= len(issues) * 20
            quality_score -= len(warnings) * 5
            quality_score = max(0, quality_score)
            
            is_valid = len(issues) == 0
            
            self.validation_results['activity'] = {
                'is_valid': is_valid,
                'issues': issues,
                'warnings': warnings,
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'missing_values': int(df.isnull().sum().sum()),
                'duplicate_rows': len(df[df.duplicated()]),
                'quality_score': quality_score
            }
            self.quality_scores['activity'] = quality_score
            
            logger.info(f"✓ Activity validation: {'PASSED' if is_valid else 'FAILED'} (Score: {quality_score:.1f}%)")
            return is_valid, issues + warnings, quality_score
        except Exception as e:
            logger.error(f"✗ Error validating activity: {str(e)}")
            return False, [str(e)], 0
    
    def validate_all(self) -> bool:
        """
        Validate all data.
        
        Returns:
            bool: True if all validation passed
        """
        logger.info("Starting data validation...")
        logger.info("=" * 60)
        
        try:
            results = {
                'assessments': self.validate_assessments(),
                'students': self.validate_students(),
                'registrations': self.validate_registrations(),
                'assessment_results': self.validate_assessment_results(),
                'activity': self.validate_activity(),
            }
            
            all_valid = all(result[0] for result in results.values())
            overall_score = sum(self.quality_scores.values()) / len(self.quality_scores)
            
            logger.info("=" * 60)
            logger.info(f"✓ Data validation completed")
            logger.info(f"  Overall Quality Score: {overall_score:.1f}%")
            logger.info(f"  All Validations Passed: {all_valid}")
            
            # Generate validation report
            report = generate_validation_report(self.validation_results)
            report_file = REPORTS_PATH / "data_validation_report.txt"
            with open(report_file, 'w') as f:
                f.write(report)
            logger.info(f"  Report saved to: {report_file}")
            
            return all_valid
        except Exception as e:
            logger.error(f"✗ Data validation failed: {str(e)}")
            return False
    
    def get_validation_results(self) -> Dict:
        """
        Get validation results.
        
        Returns:
            Dictionary of validation results
        """
        return self.validation_results
    
    def get_quality_scores(self) -> Dict[str, float]:
        """
        Get quality scores for each dataset.
        
        Returns:
            Dictionary of quality scores
        """
        return self.quality_scores


if __name__ == "__main__":
    logger.info("Data Validator Module Loaded")
