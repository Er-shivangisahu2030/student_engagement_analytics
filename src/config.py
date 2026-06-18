"""
Configuration Module
Centralized configuration for database, logging, and ETL pipeline settings.
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# PROJECT PATHS
# ============================================================================
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW_PATH = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_PATH = PROJECT_ROOT / "data" / "processed"
LOGS_PATH = PROJECT_ROOT / "data" / "logs"
REPORTS_PATH = PROJECT_ROOT / "data" / "reports"

# Ensure directories exist
for path in [DATA_PROCESSED_PATH, LOGS_PATH, REPORTS_PATH]:
    path.mkdir(parents=True, exist_ok=True)

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
DB_CONFIG: Dict[str, Any] = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "student_engagement_db"),
    "charset": "utf8mb4",
    "autocommit": False,
    "use_unicode": True,
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_CONFIG: Dict[str, Any] = {
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "log_file": LOGS_PATH / "pipeline.log",
    "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
}

# ============================================================================
# ETL PIPELINE CONFIGURATION
# ============================================================================
ETL_CONFIG: Dict[str, Any] = {
    # Input files
    "input_files": {
        "assessments": DATA_RAW_PATH / "assessments.csv",
        "students": DATA_RAW_PATH / "studentInfo.csv",
        "registrations": DATA_RAW_PATH / "studentRegistration.csv",
        "assessment_results": DATA_RAW_PATH / "studentAssessment.csv",
        "activity": DATA_RAW_PATH / "studentActivity.csv",
    },
    
    # Output files
    "output_files": {
        "students": DATA_PROCESSED_PATH / "dim_student.csv",
        "courses": DATA_PROCESSED_PATH / "dim_course.csv",
        "registrations": DATA_PROCESSED_PATH / "fact_student_activity.csv",
        "assessments": DATA_PROCESSED_PATH / "fact_assessment.csv",
        "engagement": DATA_PROCESSED_PATH / "fact_engagement.csv",
    },
    
    # Data quality thresholds
    "quality_thresholds": {
        "max_missing_percentage": 30,
        "min_rows": 100,
        "max_duplicates_percentage": 5,
    },
    
    # Batch size for database operations
    "batch_size": 1000,
    "chunk_size": 5000,
}

# ============================================================================
# COLUMN MAPPINGS & STANDARDS
# ============================================================================
COLUMN_NAMING_STANDARD = "snake_case"

VALID_ASSESSMENT_TYPES = ["TMA", "Exam", "CMA"]
VALID_EDUCATION_LEVELS = ["A Level", "HE Qualification", "Lower Than A Level", "Post Graduate Qualification"]
VALID_FINAL_RESULTS = ["Distinction", "Credit", "Pass", "Fail", "Withdrawn"]
VALID_REGIONS = [
    "East Anglia", "East Midlands", "London", "Midlands", "North Eastern",
    "North Western", "Northern Scotland", "South", "South West", "Southern Scotland",
    "Wales", "West Midlands"
]

# ============================================================================
# ANALYTICS CONFIGURATION
# ============================================================================
ANALYTICS_CONFIG: Dict[str, Any] = {
    "engagement_score_weights": {
        "activity_frequency": 0.3,
        "assessment_completion": 0.4,
        "score_performance": 0.3,
    },
    "risk_thresholds": {
        "low": (70, 100),
        "medium": (50, 70),
        "high": (0, 50),
    },
    "streak_definitions": {
        "min_days_active": 7,
        "activity_threshold": 10,
    },
}

# ============================================================================
# FILE ENCODING & FORMATS
# ============================================================================
FILE_CONFIG: Dict[str, Any] = {
    "encoding": "utf-8",
    "csv_separator": ",",
    "date_format": "%Y-%m-%d",
    "timestamp_format": "%Y-%m-%d %H:%M:%S",
}

# ============================================================================
# VALIDATION RULES
# ============================================================================
VALIDATION_RULES: Dict[str, Dict[str, Any]] = {
    "studentInfo": {
        "required_columns": ["id_student", "gender", "region", "highest_education", "imd_band", "age_band"],
        "data_types": {"id_student": int, "gender": str},
    },
    "assessments": {
        "required_columns": ["code_module", "code_presentation", "id_assessment", "assessment_type", "weight"],
        "data_types": {"id_assessment": int, "weight": float},
    },
    "studentRegistration": {
        "required_columns": ["id_student", "code_module", "code_presentation", "final_result"],
        "data_types": {"id_student": int},
    },
    "studentAssessment": {
        "required_columns": ["id_student", "id_assessment", "score"],
        "data_types": {"id_student": int, "id_assessment": int, "score": float},
    },
    "studentActivity": {
        "required_columns": ["id_student", "code_module", "date", "sum_click"],
        "data_types": {"id_student": int, "date": int, "sum_click": int},
    },
}

# ============================================================================
# STREAMLIT CONFIGURATION
# ============================================================================
STREAMLIT_CONFIG: Dict[str, Any] = {
    "page_title": "Student Engagement & Learning Streak Analytics",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def get_db_connection_string() -> str:
    """Generate MySQL connection string."""
    return (f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
            f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")


def get_log_file_path() -> Path:
    """Get the full path to the log file."""
    return LOG_CONFIG["log_file"]


if __name__ == "__main__":
    print("Configuration Module")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Data Raw Path: {DATA_RAW_PATH}")
    print(f"Database: {DB_CONFIG['database']}")
    print(f"Log Level: {LOG_CONFIG['log_level']}")
