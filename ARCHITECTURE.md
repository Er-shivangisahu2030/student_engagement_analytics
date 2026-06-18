# 🏗️ System Architecture & Design Documentation

## Project Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Data Sources                                       │
│            (CSV Files - OULAD Dataset)                               │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    EXTRACT LAYER                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ • Read CSV files                                             │  │
│  │ • Handle multiple data sources                               │  │
│  │ • Normalize column names                                     │  │
│  │ • Initial row counts                                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   CLEAN LAYER                                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ • Remove duplicates                                          │  │
│  │ • Handle missing values                                      │  │
│  │ • Standardize data types                                     │  │
│  │ • Remove invalid records                                     │  │
│  │ • Normalize categorical values                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 VALIDATE LAYER                                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ • Data quality checks                                        │  │
│  │ • Schema validation                                          │  │
│  │ • Range validation                                           │  │
│  │ • Missing value analysis                                     │  │
│  │ • Quality scoring (0-100)                                    │  │
│  │ • Generate validation reports                                │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                TRANSFORM LAYER                                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Star Schema Transformation:                                  │  │
│  │                                                               │  │
│  │ Dimension Tables:                                            │  │
│  │  • dim_student (200 students)                                │  │
│  │  • dim_course (12+ courses)                                  │  │
│  │  • dim_assessment (200+ assessments)                         │  │
│  │                                                               │  │
│  │ Fact Tables:                                                 │  │
│  │  • fact_assessment (13,994 records)                          │  │
│  │  • fact_learning_activity (426,869 records)                  │  │
│  │  • fact_engagement (1,522 records)                           │  │
│  │                                                               │  │
│  │ Calculated Metrics:                                          │  │
│  │  • Engagement Score (0-100)                                  │  │
│  │  • Learning Streak (days)                                    │  │
│  │  • Risk Level (Low/Medium/High)                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  LOAD LAYER                                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ • Create database schema                                     │  │
│  │ • Bulk insert into MySQL                                     │  │
│  │ • Create indexes                                             │  │
│  │ • Establish relationships                                    │  │
│  │ • Record execution metadata                                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│            MySQL Data Warehouse                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Dimension Tables  │  Fact Tables  │  Views  │  Procedures   │  │
│  │ ─────────────────────────────────────────────────────────── │  │
│  │ • dim_student     │ fact_assessment       │ vw_engagement   │  │
│  │ • dim_course      │ fact_learning_activity│ vw_at_risk      │  │
│  │ • dim_assessment  │ fact_engagement       │ vw_streaks      │  │
│  │                   │                       │ vw_regional     │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│          Streamlit Analytics Dashboard                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ • Real-time KPI cards                                        │  │
│  │ • Interactive charts & visualizations                        │  │
│  │ • Student search & filtering                                 │  │
│  │ • Course analytics                                           │  │
│  │ • At-risk student identification                             │  │
│  │ • Learning streak analysis                                   │  │
│  │ • Pipeline status & data quality                             │  │
│  │ • CSV export functionality                                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
Raw Data Files
     │
     ├─ assessments.csv
     ├─ studentInfo.csv
     ├─ studentRegistration.csv
     ├─ studentAssessment.csv
     └─ studentActivity.csv
     │
     ▼
┌──────────────────────┐
│  DataExtractor       │  Normalize columns
│  extract.py          │  Handle encoding
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  DataCleaner         │  Remove duplicates
│  data_cleaning.py    │  Fill missing values
└──────────┬───────────┘  Standardize values
           │
           ▼
┌──────────────────────┐
│  DataValidator       │  Quality checks
│  data_validation.py  │  Generate reports
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  DataTransformer     │  Create dimensions
│  data_transform.py   │  Create facts
└──────────┬───────────┘  Calculate metrics
           │
           ▼
┌──────────────────────┐
│  DataLoader          │  Bulk insert
│  data_load.py        │  Create indexes
└──────────┬───────────┘  Log execution
           │
           ▼
    MySQL Database
```

## Module Dependencies

```
src/
├── config.py                   (Configuration)
│   └── Used by all modules
│
├── utils/
│   ├── logger.py              (Logging)
│   │   └── Used by all modules
│   └── helpers.py             (Utilities)
│       └── Used by ETL modules
│
├── database/
│   ├── connection.py          (DB Connection)
│   │   └── Used by schema.py, data_load.py
│   └── schema.py              (Schema Generation)
│       └── Used by main_pipeline.py
│
├── etl/
│   ├── extract.py             (Extract)
│   │   └── Used by main_pipeline.py
│   ├── data_cleaning.py       (Clean)
│   │   └── Depends on extract.py
│   ├── data_validation.py     (Validate)
│   │   └── Depends on data_cleaning.py
│   ├── data_transform.py      (Transform)
│   │   └── Depends on data_validation.py
│   └── data_load.py           (Load)
│       └── Depends on data_transform.py
│
├── pipeline/
│   └── main_pipeline.py       (Orchestration)
│       └── Orchestrates all ETL modules
│
├── analytics/
│   └── metrics.py             (Analytics)
│       └── Used by dashboard
│
└── dashboard/
    └── streamlit_app.py       (Dashboard)
        └── Displays data from database
```

## Star Schema Design

### Dimension Tables

```
dim_student
├── student_key (PK)
├── id_student (Business Key)
├── gender
├── region (12 regions)
├── highest_education
├── imd_band (IMD quintiles)
├── age_band (Age groups)
├── enrollment_year
└── is_active

dim_course
├── course_key (PK)
├── code_module (Business Key)
├── code_presentation (Business Key)
├── course_name
├── course_year
├── course_semester
├── course_level
└── is_active

dim_assessment
├── assessment_key (PK)
├── id_assessment (Business Key)
├── code_module
├── code_presentation
├── assessment_type (TMA, Exam, CMA)
├── assessment_due_date
└── assessment_weight
```

### Fact Tables

```
fact_engagement (1,522 records)
├── engagement_record_key (PK)
├── id_student (FK)
├── code_module (FK)
├── code_presentation (FK)
├── engagement_score (0-100)
├── learning_streak (days)
├── assignment_completion_percentage (0-100)
├── average_assessment_score (0-100)
├── attendance_count
├── days_since_last_activity
├── risk_level (Low/Medium/High)
├── is_at_risk (Boolean)
├── final_result
└── timestamps

fact_assessment (13,994 records)
├── assessment_record_key (PK)
├── id_student (FK)
├── id_assessment (FK)
├── code_module (FK)
├── score (0-100)
├── is_submitted (Boolean)
├── is_banked (Boolean)
├── submission_date
├── assessment_status
└── timestamps

fact_learning_activity (426,869 records)
├── activity_record_key (PK)
├── id_student (FK)
├── code_module (FK)
├── code_presentation (FK)
├── activity_date (days since course start)
├── activity_type (Lecture, Tutorial, etc)
├── click_count
├── time_spent_minutes
├── is_assignment_related (Boolean)
└── timestamps
```

## Metrics Calculation Logic

### Engagement Score Formula
```
Engagement Score = (AF × 0.3) + (AC × 0.4) + (SP × 0.3)

Where:
AF = Activity Frequency Score (normalized clicks)
AC = Assignment Completion % (0-100)
SP = Score Performance (avg assessment score as %)
```

### Learning Streak Calculation
```
Streak = Maximum consecutive days with activity
Example: Days active [1,2,3,4,5,10,11,12] → Streak = 5
```

### Risk Level Determination
```
Low Risk:    Engagement ≥ 70 AND Score ≥ 65
Medium Risk: Engagement 40-70 OR Score 40-65
High Risk:   Engagement < 40 AND Score < 40
```

## Performance Optimization Strategies

### 1. Indexing Strategy
```sql
-- Composite indexes for common queries
CREATE INDEX idx_student_course_date 
    ON fact_learning_activity(id_student, code_module, activity_date);

CREATE INDEX idx_engagement_risk_at_risk
    ON fact_engagement(id_student, risk_level, is_at_risk);

-- Single column indexes for filtering
CREATE INDEX idx_is_at_risk ON fact_engagement(is_at_risk);
CREATE INDEX idx_risk_level ON fact_engagement(risk_level);
```

### 2. Batch Processing
```python
batch_size = 1000  # Process 1000 rows at a time
chunk_size = 5000  # Activity data in 5000-row chunks
```

### 3. Connection Pooling
```python
pool_size = 5  # Maintain 5 database connections
pool_recycle = 3600  # Recycle connections every hour
```

### 4. Caching Strategy
- @st.cache_data decorator for Streamlit
- 24-hour cache for summary statistics
- Real-time cache for recent queries

## Error Handling & Recovery

### Logging Levels
```
DEBUG   → Detailed diagnostic information
INFO    → General informational messages
WARNING → Warning messages about potential issues
ERROR   → Error messages
CRITICAL → Critical errors requiring attention
```

### Retry Mechanism
```python
max_retries = 3
retry_delay = 5  # seconds
```

### Transaction Management
```python
autocommit = False  # Explicit commit control
rollback on error   # Automatic rollback
```

## Security Considerations

1. **Database Credentials**
   - Store in .env file (never commit)
   - Use environment variables
   - Rotate credentials regularly

2. **Data Access Control**
   - MySQL user with limited permissions
   - Database-level access control
   - Audit logging of all operations

3. **Input Validation**
   - All CSV inputs validated
   - SQL injection prevention via parameterized queries
   - Type checking throughout pipeline

## Scalability Considerations

### Horizontal Scaling
- Separate ETL from dashboard on different servers
- MySQL replication for read-heavy workloads
- Load balancer for Streamlit instances

### Vertical Scaling
- Increase MySQL memory allocation
- Optimize query execution plans
- Use SSD storage for database

### Data Volume
- Current: ~427,000 rows across 5 tables
- Handles: 1M+ rows efficiently
- Partitioning strategy for larger datasets

## Monitoring & Alerting

### Pipeline Monitoring
- Execution time tracking
- Error count monitoring
- Data quality score trending

### Database Monitoring
- Query performance metrics
- Index usage statistics
- Connection pool utilization

### Dashboard Monitoring
- Page load times
- User session tracking
- Error rate monitoring
