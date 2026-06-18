"""
Schema Module
Generates and manages database schema for the analytics platform.
"""

import logging
from pathlib import Path
from typing import List

from database.connection import db_connection
from config import PROJECT_ROOT


logger = logging.getLogger(__name__)


class SchemaGenerator:
    """
    Generates SQL schema for the star schema data warehouse.
    """
    
    @staticmethod
    def generate_schema_sql() -> str:
        """
        Generate complete SQL schema for the analytics platform.
        
        Returns:
            SQL schema as string
        """
        schema = """
-- ============================================================================
-- STUDENT ENGAGEMENT & LEARNING STREAK ANALYTICS PLATFORM
-- Star Schema Database Design
-- ============================================================================

-- ============================================================================
-- DIMENSION TABLES
-- ============================================================================

-- Student Dimension
CREATE TABLE IF NOT EXISTS dim_student (
    student_key INT PRIMARY KEY AUTO_INCREMENT,
    id_student INT UNIQUE NOT NULL,
    gender VARCHAR(10),
    region VARCHAR(100),
    highest_education VARCHAR(100),
    imd_band VARCHAR(20),
    age_band VARCHAR(20),
    enrollment_year INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_id_student (id_student),
    INDEX idx_region (region),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Course Dimension
CREATE TABLE IF NOT EXISTS dim_course (
    course_key INT PRIMARY KEY AUTO_INCREMENT,
    code_module VARCHAR(20) NOT NULL,
    code_presentation VARCHAR(20) NOT NULL,
    course_name VARCHAR(255),
    course_year INT,
    course_semester VARCHAR(10),
    course_level VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_course (code_module, code_presentation),
    INDEX idx_code_module (code_module),
    INDEX idx_course_year (course_year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Assessment Dimension
CREATE TABLE IF NOT EXISTS dim_assessment (
    assessment_key INT PRIMARY KEY AUTO_INCREMENT,
    id_assessment INT UNIQUE NOT NULL,
    code_module VARCHAR(20) NOT NULL,
    code_presentation VARCHAR(20) NOT NULL,
    assessment_type VARCHAR(50) NOT NULL,
    assessment_due_date INT,
    assessment_weight INT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_id_assessment (id_assessment),
    INDEX idx_assessment_type (assessment_type),
    FOREIGN KEY (code_module) REFERENCES dim_course(code_module)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Date Dimension
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INT PRIMARY KEY,
    date_value DATE UNIQUE NOT NULL,
    year INT,
    month INT,
    day INT,
    quarter INT,
    week_of_year INT,
    day_of_week INT,
    day_name VARCHAR(20),
    is_weekend BOOLEAN,
    
    INDEX idx_date_value (date_value),
    INDEX idx_year_month (year, month)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- FACT TABLES
-- ============================================================================

-- Fact: Student Assessment Results
CREATE TABLE IF NOT EXISTS fact_assessment (
    assessment_record_key INT PRIMARY KEY AUTO_INCREMENT,
    student_key INT NOT NULL,
    assessment_key INT NOT NULL,
    course_key INT NOT NULL,
    assessment_date_key INT,
    submission_date_key INT,
    submission_date INT,
    score FLOAT,
    is_banked BOOLEAN,
    is_submitted BOOLEAN,
    days_late INT,
    assessment_status VARCHAR(50),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_student_key (student_key),
    INDEX idx_assessment_key (assessment_key),
    INDEX idx_course_key (course_key),
    INDEX idx_assessment_status (assessment_status),
    FOREIGN KEY (student_key) REFERENCES dim_student(student_key),
    FOREIGN KEY (assessment_key) REFERENCES dim_assessment(assessment_key),
    FOREIGN KEY (course_key) REFERENCES dim_course(course_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Fact: Student Learning Activity
CREATE TABLE IF NOT EXISTS fact_learning_activity (
    activity_record_key INT PRIMARY KEY AUTO_INCREMENT,
    student_key INT NOT NULL,
    course_key INT NOT NULL,
    activity_date_key INT,
    activity_type VARCHAR(100),
    activity_date INT,
    click_count INT,
    time_spent_minutes INT,
    resource_type VARCHAR(100),
    is_assignment_related BOOLEAN,
    activity_week INT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_student_key (student_key),
    INDEX idx_course_key (course_key),
    INDEX idx_activity_type (activity_type),
    INDEX idx_activity_date (activity_date),
    INDEX idx_student_course_date (student_key, course_key, activity_date),
    FOREIGN KEY (student_key) REFERENCES dim_student(student_key),
    FOREIGN KEY (course_key) REFERENCES dim_course(course_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Fact: Student Engagement
CREATE TABLE IF NOT EXISTS fact_engagement (
    engagement_record_key INT PRIMARY KEY AUTO_INCREMENT,
    student_key INT NOT NULL,
    course_key INT NOT NULL,
    date_key INT,
    engagement_score FLOAT,
    attendance_count INT,
    days_since_last_activity INT,
    learning_streak INT,
    assignment_completion_percentage FLOAT,
    average_assessment_score FLOAT,
    risk_level VARCHAR(50),
    activity_intensity VARCHAR(50),
    last_activity_date INT,
    enrollment_date INT,
    completion_date INT,
    is_at_risk BOOLEAN,
    final_result VARCHAR(50),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_student_key (student_key),
    INDEX idx_course_key (course_key),
    INDEX idx_date_key (date_key),
    INDEX idx_risk_level (risk_level),
    INDEX idx_is_at_risk (is_at_risk),
    INDEX idx_student_course_date (student_key, course_key, date_key),
    FOREIGN KEY (student_key) REFERENCES dim_student(student_key),
    FOREIGN KEY (course_key) REFERENCES dim_course(course_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- AGGREGATE TABLES (For Performance)
-- ============================================================================

-- Student Course Daily Metrics
CREATE TABLE IF NOT EXISTS agg_student_course_daily (
    aggregate_key INT PRIMARY KEY AUTO_INCREMENT,
    student_key INT NOT NULL,
    course_key INT NOT NULL,
    date_key INT NOT NULL,
    daily_clicks INT DEFAULT 0,
    daily_assessments_submitted INT DEFAULT 0,
    daily_assessment_score FLOAT,
    daily_engagement_score FLOAT,
    is_active_day BOOLEAN DEFAULT FALSE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_daily (student_key, course_key, date_key),
    INDEX idx_student_key (student_key),
    INDEX idx_course_key (course_key),
    INDEX idx_date_key (date_key),
    FOREIGN KEY (student_key) REFERENCES dim_student(student_key),
    FOREIGN KEY (course_key) REFERENCES dim_course(course_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Course Metrics Summary
CREATE TABLE IF NOT EXISTS agg_course_metrics (
    course_key INT PRIMARY KEY,
    code_module VARCHAR(20),
    code_presentation VARCHAR(20),
    total_students INT DEFAULT 0,
    active_students INT DEFAULT 0,
    avg_engagement_score FLOAT,
    avg_assessment_completion FLOAT,
    at_risk_students INT DEFAULT 0,
    completion_rate FLOAT,
    avg_final_score FLOAT,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_code_module (code_module),
    FOREIGN KEY (course_key) REFERENCES dim_course(course_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- METADATA & AUDIT TABLES
-- ============================================================================

-- Pipeline Execution Log
CREATE TABLE IF NOT EXISTS pipeline_execution_log (
    execution_id INT PRIMARY KEY AUTO_INCREMENT,
    pipeline_name VARCHAR(255) NOT NULL,
    execution_status VARCHAR(50) NOT NULL,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    total_rows_extracted INT DEFAULT 0,
    total_rows_cleaned INT DEFAULT 0,
    total_rows_loaded INT DEFAULT 0,
    total_errors INT DEFAULT 0,
    total_warnings INT DEFAULT 0,
    execution_duration_seconds FLOAT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_pipeline_name (pipeline_name),
    INDEX idx_execution_status (execution_status),
    INDEX idx_start_time (start_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Data Quality Report
CREATE TABLE IF NOT EXISTS data_quality_report (
    report_id INT PRIMARY KEY AUTO_INCREMENT,
    file_name VARCHAR(255) NOT NULL,
    validation_status VARCHAR(50) NOT NULL,
    total_rows INT DEFAULT 0,
    total_columns INT DEFAULT 0,
    missing_values INT DEFAULT 0,
    duplicate_rows INT DEFAULT 0,
    quality_score FLOAT,
    validation_details TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_file_name (file_name),
    INDEX idx_validation_status (validation_status),
    INDEX idx_created_date (created_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_fact_assessment_student_course 
    ON fact_assessment(student_key, course_key, assessment_date_key);

CREATE INDEX IF NOT EXISTS idx_fact_activity_student_course_date 
    ON fact_learning_activity(student_key, course_key, activity_date);

CREATE INDEX IF NOT EXISTS idx_fact_engagement_multi 
    ON fact_engagement(student_key, course_key, risk_level, is_at_risk);

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
"""
        return schema
    
    @staticmethod
    def create_schema(db: object) -> bool:
        """
        Create database schema.
        
        Args:
            db: Database connection object
        
        Returns:
            bool: True if successful
        """
        try:
            # Create database if it doesn't exist
            db.create_database()
            
            # Generate and execute schema SQL
            schema_sql = SchemaGenerator.generate_schema_sql()
            
            # Save schema to file
            schema_file = PROJECT_ROOT / "sql" / "schema.sql"
            schema_file.parent.mkdir(parents=True, exist_ok=True)
            with open(schema_file, 'w', encoding='utf-8') as f:
                f.write(schema_sql)
            logger.info(f"Schema saved to {schema_file}")
            
            # Execute schema creation
            db.execute_sql_file(str(schema_file))
            logger.info("Database schema created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating schema: {str(e)}")
            return False
    
    @staticmethod
    def generate_views_sql() -> str:
        """
        Generate SQL for analytical views.
        
        Returns:
            SQL views as string
        """
        views = """
-- ============================================================================
-- ANALYTICAL VIEWS
-- ============================================================================

-- Student Engagement Summary View
CREATE OR REPLACE VIEW vw_student_engagement_summary AS
SELECT 
    ds.id_student,
    ds.gender,
    ds.region,
    dc.code_module,
    dc.code_presentation,
    fe.engagement_score,
    fe.learning_streak,
    fe.assignment_completion_percentage,
    fe.average_assessment_score,
    fe.risk_level,
    fe.is_at_risk,
    fe.days_since_last_activity,
    fe.final_result,
    fe.created_date
FROM fact_engagement fe
JOIN dim_student ds ON fe.student_key = ds.student_key
JOIN dim_course dc ON fe.course_key = dc.course_key
WHERE fe.is_active BOOLEAN DEFAULT TRUE;

-- Learning Streak View
CREATE OR REPLACE VIEW vw_learning_streaks AS
SELECT 
    ds.id_student,
    ds.gender,
    ds.region,
    dc.code_module,
    dc.code_presentation,
    fe.learning_streak,
    fe.engagement_score,
    fe.days_since_last_activity,
    CASE 
        WHEN fe.learning_streak >= 30 THEN 'Excellent'
        WHEN fe.learning_streak >= 20 THEN 'Good'
        WHEN fe.learning_streak >= 10 THEN 'Fair'
        ELSE 'Poor'
    END AS streak_quality
FROM fact_engagement fe
JOIN dim_student ds ON fe.student_key = ds.student_key
JOIN dim_course dc ON fe.course_key = dc.course_key
ORDER BY fe.learning_streak DESC;

-- Assignment Completion View
CREATE OR REPLACE VIEW vw_assignment_completion AS
SELECT 
    ds.id_student,
    dc.code_module,
    dc.code_presentation,
    COUNT(DISTINCT da.assessment_key) AS total_assessments,
    SUM(CASE WHEN fa.is_submitted = TRUE THEN 1 ELSE 0 END) AS submitted_assessments,
    ROUND(SUM(CASE WHEN fa.is_submitted = TRUE THEN 1 ELSE 0 END) / 
        COUNT(DISTINCT da.assessment_key) * 100, 2) AS completion_percentage,
    ROUND(AVG(fa.score), 2) AS average_score,
    MAX(fa.score) AS highest_score,
    MIN(fa.score) AS lowest_score
FROM fact_assessment fa
JOIN dim_student ds ON fa.student_key = ds.student_key
JOIN dim_assessment da ON fa.assessment_key = da.assessment_key
JOIN dim_course dc ON fa.course_key = dc.course_key
GROUP BY ds.id_student, dc.code_module, dc.code_presentation;

-- Course Engagement View
CREATE OR REPLACE VIEW vw_course_engagement AS
SELECT 
    dc.code_module,
    dc.code_presentation,
    COUNT(DISTINCT fe.student_key) AS total_students,
    SUM(CASE WHEN fe.is_at_risk = FALSE THEN 1 ELSE 0 END) AS engaged_students,
    SUM(CASE WHEN fe.is_at_risk = TRUE THEN 1 ELSE 0 END) AS at_risk_students,
    ROUND(AVG(fe.engagement_score), 2) AS avg_engagement_score,
    ROUND(AVG(fe.assignment_completion_percentage), 2) AS avg_completion_percentage,
    ROUND(AVG(fe.average_assessment_score), 2) AS avg_assessment_score,
    ROUND(AVG(fe.learning_streak), 2) AS avg_learning_streak
FROM fact_engagement fe
JOIN dim_course dc ON fe.course_key = dc.course_key
GROUP BY dc.code_module, dc.code_presentation;

-- At-Risk Students View
CREATE OR REPLACE VIEW vw_at_risk_students AS
SELECT 
    ds.id_student,
    ds.gender,
    ds.region,
    ds.age_band,
    ds.highest_education,
    dc.code_module,
    dc.code_presentation,
    fe.engagement_score,
    fe.risk_level,
    fe.learning_streak,
    fe.assignment_completion_percentage,
    fe.average_assessment_score,
    fe.days_since_last_activity,
    CASE 
        WHEN fe.engagement_score < 30 AND fe.average_assessment_score < 40 THEN 'Critical'
        WHEN fe.engagement_score < 50 OR fe.average_assessment_score < 50 THEN 'High'
        WHEN fe.days_since_last_activity > 14 THEN 'Medium'
        ELSE 'Low'
    END AS risk_priority
FROM fact_engagement fe
JOIN dim_student ds ON fe.student_key = ds.student_key
JOIN dim_course dc ON fe.course_key = dc.course_key
WHERE fe.is_at_risk = TRUE;

-- Student Activity Frequency View
CREATE OR REPLACE VIEW vw_student_activity_frequency AS
SELECT 
    ds.id_student,
    dc.code_module,
    dc.code_presentation,
    DATE(fla.activity_date) AS activity_date,
    COUNT(*) AS total_activities,
    SUM(fla.click_count) AS total_clicks,
    ROUND(AVG(fla.click_count), 2) AS avg_clicks_per_activity,
    COUNT(DISTINCT fla.activity_type) AS unique_activity_types
FROM fact_learning_activity fla
JOIN dim_student ds ON fla.student_key = ds.student_key
JOIN dim_course dc ON fla.course_key = dc.course_key
GROUP BY ds.id_student, dc.code_module, dc.code_presentation, DATE(fla.activity_date);

-- Regional Engagement Statistics View
CREATE OR REPLACE VIEW vw_regional_engagement_stats AS
SELECT 
    ds.region,
    COUNT(DISTINCT ds.student_key) AS total_students,
    ROUND(AVG(fe.engagement_score), 2) AS avg_engagement_score,
    ROUND(AVG(fe.assignment_completion_percentage), 2) AS avg_completion_percentage,
    SUM(CASE WHEN fe.is_at_risk = TRUE THEN 1 ELSE 0 END) AS at_risk_count,
    ROUND(SUM(CASE WHEN fe.is_at_risk = TRUE THEN 1 ELSE 0 END) / 
        COUNT(DISTINCT ds.student_key) * 100, 2) AS at_risk_percentage
FROM fact_engagement fe
JOIN dim_student ds ON fe.student_key = ds.student_key
WHERE ds.region IS NOT NULL
GROUP BY ds.region;

-- ============================================================================
-- END OF VIEWS
-- ============================================================================
"""
        return views
    
    @staticmethod
    def create_views(db: object) -> bool:
        """
        Create analytical views.
        
        Args:
            db: Database connection object
        
        Returns:
            bool: True if successful
        """
        try:
            views_sql = SchemaGenerator.generate_views_sql()
            
            # Save views to file
            views_file = PROJECT_ROOT / "sql" / "views.sql"
            views_file.parent.mkdir(parents=True, exist_ok=True)
            with open(views_file, 'w', encoding='utf-8') as f:
                f.write(views_sql)
            logger.info(f"Views saved to {views_file}")
            
            # Execute views creation
            db.execute_sql_file(str(views_file))
            logger.info("Database views created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating views: {str(e)}")
            return False


if __name__ == "__main__":
    schema_gen = SchemaGenerator()
    print("Schema Generator Module Loaded")
