-- ============================================================================
-- STUDENT ENGAGEMENT & LEARNING STREAK ANALYTICS PLATFORM
-- Complete SQL Schema with Views and Stored Procedures
-- ============================================================================

-- ============================================================================
-- DATABASE CREATION
-- ============================================================================

CREATE DATABASE IF NOT EXISTS student_engagement_db 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE student_engagement_db;

-- ============================================================================
-- DIMENSION TABLES
-- ============================================================================

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
    INDEX idx_assessment_type (assessment_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- FACT TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS fact_assessment (
    assessment_record_key INT PRIMARY KEY AUTO_INCREMENT,
    id_student INT NOT NULL,
    id_assessment INT NOT NULL,
    code_module VARCHAR(20),
    code_presentation VARCHAR(20),
    submission_date INT,
    score FLOAT,
    is_banked BOOLEAN,
    is_submitted BOOLEAN,
    days_late INT,
    assessment_status VARCHAR(50),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_id_student (id_student),
    INDEX idx_id_assessment (id_assessment),
    INDEX idx_assessment_status (assessment_status),
    INDEX idx_composite (id_student, code_module)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS fact_learning_activity (
    activity_record_key INT PRIMARY KEY AUTO_INCREMENT,
    id_student INT NOT NULL,
    code_module VARCHAR(20),
    code_presentation VARCHAR(20),
    activity_date INT,
    activity_type VARCHAR(100),
    click_count INT,
    time_spent_minutes INT,
    resource_type VARCHAR(100),
    is_assignment_related BOOLEAN,
    activity_week INT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_id_student (id_student),
    INDEX idx_activity_type (activity_type),
    INDEX idx_activity_date (activity_date),
    INDEX idx_composite (id_student, code_module, activity_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS fact_engagement (
    engagement_record_key INT PRIMARY KEY AUTO_INCREMENT,
    id_student INT NOT NULL,
    code_module VARCHAR(20),
    code_presentation VARCHAR(20),
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
    
    INDEX idx_id_student (id_student),
    INDEX idx_code_module (code_module),
    INDEX idx_risk_level (risk_level),
    INDEX idx_is_at_risk (is_at_risk),
    INDEX idx_composite (id_student, code_module, risk_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- AUDIT & METADATA TABLES
-- ============================================================================

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
    INDEX idx_validation_status (validation_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- ANALYTICAL VIEWS
-- ============================================================================

CREATE OR REPLACE VIEW vw_student_engagement_summary AS
SELECT 
    ds.id_student,
    ds.gender,
    ds.region,
    fe.code_module,
    fe.code_presentation,
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
JOIN dim_student ds ON fe.id_student = ds.id_student
ORDER BY fe.engagement_score DESC;

CREATE OR REPLACE VIEW vw_learning_streaks AS
SELECT 
    ds.id_student,
    ds.gender,
    ds.region,
    fe.code_module,
    fe.code_presentation,
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
JOIN dim_student ds ON fe.id_student = ds.id_student
ORDER BY fe.learning_streak DESC;

CREATE OR REPLACE VIEW vw_assignment_completion AS
SELECT 
    ds.id_student,
    fe.code_module,
    fe.code_presentation,
    COUNT(DISTINCT fa.id_assessment) AS total_assessments,
    SUM(CASE WHEN fa.is_submitted = TRUE THEN 1 ELSE 0 END) AS submitted_assessments,
    ROUND(fe.assignment_completion_percentage, 2) AS completion_percentage,
    ROUND(fe.average_assessment_score, 2) AS average_score,
    MAX(fa.score) AS highest_score,
    MIN(fa.score) AS lowest_score
FROM fact_engagement fe
LEFT JOIN dim_student ds ON fe.id_student = ds.id_student
LEFT JOIN fact_assessment fa ON fe.id_student = fa.id_student AND fe.code_module = fa.code_module
GROUP BY ds.id_student, fe.code_module, fe.code_presentation;

CREATE OR REPLACE VIEW vw_course_engagement AS
SELECT 
    dc.code_module,
    dc.code_presentation,
    COUNT(DISTINCT fe.id_student) AS total_students,
    SUM(CASE WHEN fe.is_at_risk = FALSE THEN 1 ELSE 0 END) AS engaged_students,
    SUM(CASE WHEN fe.is_at_risk = TRUE THEN 1 ELSE 0 END) AS at_risk_students,
    ROUND(AVG(fe.engagement_score), 2) AS avg_engagement_score,
    ROUND(AVG(fe.assignment_completion_percentage), 2) AS avg_completion_percentage,
    ROUND(AVG(fe.average_assessment_score), 2) AS avg_assessment_score,
    ROUND(AVG(fe.learning_streak), 2) AS avg_learning_streak
FROM fact_engagement fe
JOIN dim_course dc ON fe.code_module = dc.code_module
GROUP BY dc.code_module, dc.code_presentation;

CREATE OR REPLACE VIEW vw_at_risk_students AS
SELECT 
    ds.id_student,
    ds.gender,
    ds.region,
    ds.age_band,
    ds.highest_education,
    fe.code_module,
    fe.code_presentation,
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
JOIN dim_student ds ON fe.id_student = ds.id_student
WHERE fe.is_at_risk = TRUE;

CREATE OR REPLACE VIEW vw_regional_engagement_stats AS
SELECT 
    ds.region,
    COUNT(DISTINCT ds.id_student) AS total_students,
    ROUND(AVG(fe.engagement_score), 2) AS avg_engagement_score,
    ROUND(AVG(fe.assignment_completion_percentage), 2) AS avg_completion_percentage,
    SUM(CASE WHEN fe.is_at_risk = TRUE THEN 1 ELSE 0 END) AS at_risk_count,
    ROUND(SUM(CASE WHEN fe.is_at_risk = TRUE THEN 1 ELSE 0 END) / 
        COUNT(DISTINCT ds.id_student) * 100, 2) AS at_risk_percentage
FROM fact_engagement fe
JOIN dim_student ds ON fe.id_student = ds.id_student
WHERE ds.region IS NOT NULL AND ds.region != 'Unknown'
GROUP BY ds.region
ORDER BY avg_engagement_score DESC;

-- ============================================================================
-- STORED PROCEDURES FOR ANALYTICS
-- ============================================================================

-- Refresh engagement metrics daily
DELIMITER //

CREATE PROCEDURE sp_refresh_daily_metrics()
BEGIN
    DECLARE v_execution_date DATE;
    SET v_execution_date = CURDATE();
    
    -- Update engagement scores
    UPDATE fact_engagement fe
    SET 
        fe.engagement_score = (
            SELECT 
                COALESCE(AVG(CASE 
                    WHEN fla.click_count > 0 THEN (fla.click_count / 100) * 30
                    ELSE 0 
                END), 0) * 0.3 +
                COALESCE(fe.assignment_completion_percentage, 0) * 0.4 +
                COALESCE((fe.average_assessment_score / 100) * 100, 0) * 0.3
            FROM fact_learning_activity fla
            WHERE fla.id_student = fe.id_student 
            AND fla.code_module = fe.code_module
        )
    WHERE fe.created_date >= DATE_SUB(v_execution_date, INTERVAL 1 DAY);
    
    -- Update risk levels
    UPDATE fact_engagement
    SET risk_level = CASE
        WHEN engagement_score >= 70 THEN 'Low'
        WHEN engagement_score >= 40 THEN 'Medium'
        ELSE 'High'
    END,
    is_at_risk = CASE
        WHEN engagement_score < 60 THEN TRUE
        ELSE FALSE
    END
    WHERE created_date >= DATE_SUB(v_execution_date, INTERVAL 1 DAY);
    
END //

DELIMITER ;

-- Get student at-risk details
DELIMITER //

CREATE PROCEDURE sp_get_at_risk_details(IN p_course_module VARCHAR(20))
BEGIN
    SELECT 
        ds.id_student,
        ds.gender,
        ds.region,
        fe.engagement_score,
        fe.risk_level,
        fe.learning_streak,
        fe.assignment_completion_percentage,
        fe.average_assessment_score,
        fe.days_since_last_activity,
        COUNT(fa.id_assessment) as total_assessments,
        SUM(CASE WHEN fa.is_submitted THEN 1 ELSE 0 END) as submitted_assessments
    FROM fact_engagement fe
    JOIN dim_student ds ON fe.id_student = ds.id_student
    LEFT JOIN fact_assessment fa ON fe.id_student = fa.id_student 
        AND fe.code_module = fa.code_module
    WHERE fe.code_module = p_course_module
    AND fe.is_at_risk = TRUE
    GROUP BY fe.id_student, fe.code_module
    ORDER BY fe.engagement_score ASC;
END //

DELIMITER ;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_fact_assessment_multi 
    ON fact_assessment(id_student, code_module, is_submitted);

CREATE INDEX IF NOT EXISTS idx_fact_activity_multi 
    ON fact_learning_activity(id_student, code_module, activity_date);

CREATE INDEX IF NOT EXISTS idx_fact_engagement_multi 
    ON fact_engagement(id_student, code_module, risk_level, is_at_risk);

-- ============================================================================
-- END OF SQL SCHEMA
-- ============================================================================
