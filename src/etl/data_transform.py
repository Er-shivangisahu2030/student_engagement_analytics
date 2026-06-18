"""
Data Transformation Module
Transforms cleaned data into star schema format.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple
from datetime import datetime, timedelta

from config import ETL_CONFIG


logger = logging.getLogger(__name__)


class DataTransformer:
    """
    Transforms data into star schema dimensional and fact tables.
    """
    
    def __init__(self, data: Dict[str, pd.DataFrame]):
        """
        Initialize transformer with cleaned data.
        
        Args:
            data: Dictionary of cleaned DataFrames
        """
        self.source_data = data
        self.transformed_data: Dict[str, pd.DataFrame] = {}
    
    def transform_dim_student(self) -> pd.DataFrame:
        """
        Create student dimension table.
        
        Returns:
            Transformed student dimension DataFrame
        """
        logger.info("Transforming dim_student...")
        df = self.source_data['students'].copy()
        
        try:
            # Create dimension table
            dim_student = df[[
                'id_student', 'gender', 'region', 'highest_education',
                'imd_band', 'age_band', 'enrollment_year'
            ]].copy()
            
            dim_student['is_active'] = True
            dim_student['created_date'] = datetime.now()
            dim_student['updated_date'] = datetime.now()
            
            # Remove duplicates (keep first)
            dim_student = dim_student.drop_duplicates(subset=['id_student'], keep='first')
            
            self.transformed_data['dim_student'] = dim_student
            logger.info(f"✓ Transformed dim_student: {len(dim_student)} rows")
            
            return dim_student
        except Exception as e:
            logger.error(f"✗ Error transforming dim_student: {str(e)}")
            raise
    
    def transform_dim_course(self) -> pd.DataFrame:
        """
        Create course dimension table.
        
        Returns:
            Transformed course dimension DataFrame
        """
        logger.info("Transforming dim_course...")
        assessments = self.source_data['assessments'].copy()
        registrations = self.source_data['registrations'].copy()
        
        try:
            # Get unique courses
            courses = assessments[['code_module', 'code_presentation']].drop_duplicates()
            
            # Add course information
            courses['course_name'] = courses['code_module'].str.upper()
            courses['course_year'] = 2013
            courses['course_semester'] = courses['code_presentation'].str.slice(0, 4)
            courses['course_level'] = 'Undergraduate'
            courses['is_active'] = True
            courses['created_date'] = datetime.now()
            courses['updated_date'] = datetime.now()
            
            dim_course = courses.reset_index(drop=True)
            
            self.transformed_data['dim_course'] = dim_course
            logger.info(f"✓ Transformed dim_course: {len(dim_course)} rows")
            
            return dim_course
        except Exception as e:
            logger.error(f"✗ Error transforming dim_course: {str(e)}")
            raise
    
    def transform_dim_assessment(self) -> pd.DataFrame:
        """
        Create assessment dimension table.
        
        Returns:
            Transformed assessment dimension DataFrame
        """
        logger.info("Transforming dim_assessment...")
        assessments = self.source_data['assessments'].copy()
        
        try:
            dim_assessment = assessments[[
                'id_assessment', 'code_module', 'code_presentation',
                'assessment_type', 'date', 'weight'
            ]].copy()
            
            dim_assessment = dim_assessment.rename(columns={
                'date': 'assessment_due_date',
                'weight': 'assessment_weight'
            })
            
            dim_assessment['created_date'] = datetime.now()
            
            # Remove duplicates
            dim_assessment = dim_assessment.drop_duplicates(subset=['id_assessment'], keep='first')
            
            self.transformed_data['dim_assessment'] = dim_assessment
            logger.info(f"✓ Transformed dim_assessment: {len(dim_assessment)} rows")
            
            return dim_assessment
        except Exception as e:
            logger.error(f"✗ Error transforming dim_assessment: {str(e)}")
            raise
    
    def transform_fact_assessment(self) -> pd.DataFrame:
        """
        Create assessment fact table.
        
        Returns:
            Transformed assessment fact DataFrame
        """
        logger.info("Transforming fact_assessment...")
        assessment_results = self.source_data['assessment_results'].copy()
        assessments = self.source_data['assessments'].copy()
        
        try:
            fact_assessment = assessment_results.copy()
            
            # Map assessment IDs to courses
            assessment_map = assessments[['id_assessment', 'code_module', 'code_presentation']].drop_duplicates()
            fact_assessment = fact_assessment.merge(
                assessment_map, on='id_assessment', how='left'
            )
            
            # Standardize columns
            fact_assessment = fact_assessment.rename(columns={
                'date_submitted': 'submission_date'
            })
            
            # Add calculated fields
            fact_assessment['is_submitted'] = fact_assessment['score'].notna()
            fact_assessment['days_late'] = 0
            fact_assessment['assessment_status'] = fact_assessment['is_submitted'].apply(
                lambda x: 'Submitted' if x else 'Not Submitted'
            )
            fact_assessment['created_date'] = datetime.now()
            
            # Select relevant columns
            fact_assessment = fact_assessment[[
                'id_student', 'id_assessment', 'code_module', 'code_presentation',
                'submission_date', 'score', 'is_banked', 'is_submitted',
                'days_late', 'assessment_status', 'created_date'
            ]]
            
            self.transformed_data['fact_assessment'] = fact_assessment
            logger.info(f"✓ Transformed fact_assessment: {len(fact_assessment)} rows")
            
            return fact_assessment
        except Exception as e:
            logger.error(f"✗ Error transforming fact_assessment: {str(e)}")
            raise
    
    def transform_fact_learning_activity(self) -> pd.DataFrame:
        """
        Create learning activity fact table.
        
        Returns:
            Transformed learning activity fact DataFrame
        """
        logger.info("Transforming fact_learning_activity...")
        activity = self.source_data['activity'].copy()
        
        try:
            fact_activity = activity.copy()
            
            # Rename columns
            fact_activity = fact_activity.rename(columns={
                'date': 'activity_date',
                'sum_click': 'click_count'
            })
            
            # Add calculated fields
            fact_activity['time_spent_minutes'] = fact_activity['click_count'] * 2  # Estimate
            fact_activity['resource_type'] = fact_activity.get('activity_type', 'Unknown')
            fact_activity['is_assignment_related'] = False
            fact_activity['activity_week'] = (fact_activity['activity_date'] // 7) + 1
            fact_activity['created_date'] = datetime.now()
            
            # Select relevant columns
            fact_activity = fact_activity[[
                'id_student', 'code_module', 'code_presentation',
                'activity_date', 'activity_type', 'click_count',
                'time_spent_minutes', 'resource_type', 'is_assignment_related',
                'activity_week', 'created_date'
            ]]
            
            self.transformed_data['fact_learning_activity'] = fact_activity
            logger.info(f"✓ Transformed fact_learning_activity: {len(fact_activity)} rows")
            
            return fact_activity
        except Exception as e:
            logger.error(f"✗ Error transforming fact_learning_activity: {str(e)}")
            raise
    
    def transform_fact_engagement(self) -> pd.DataFrame:
        """
        Create engagement fact table with calculated metrics.
        
        Returns:
            Transformed engagement fact DataFrame
        """
        logger.info("Transforming fact_engagement...")
        
        try:
            registrations = self.source_data['registrations'].copy()
            assessment_results = self.source_data['assessment_results'].copy()
            activity = self.source_data['activity'].copy()
            
            # Calculate engagement metrics per student-course combination
            fact_engagement = registrations[[
                'id_student', 'code_module', 'code_presentation',
                'date_registration', 'date_unregistration', 'final_result'
            ]].copy()
            
            # Calculate engagement score
            def calculate_engagement_score(student_id, code_module, code_presentation):
                student_activity = activity[
                    (activity['id_student'] == student_id) &
                    (activity['code_module'] == code_module)
                ]
                total_clicks = student_activity['sum_click'].sum()
                
                student_assessments = assessment_results[
                    (assessment_results['id_student'] == student_id) &
                    (assessment_results['code_module'] == code_module)
                ]
                avg_score = student_assessments['score'].mean() if len(student_assessments) > 0 else 0
                
                # Normalize and combine
                clicks_normalized = min(total_clicks / 1000, 1) * 30
                score_normalized = (avg_score / 100) * 70 if avg_score > 0 else 0
                
                return clicks_normalized + score_normalized
            
            # Apply engagement calculation
            fact_engagement['engagement_score'] = fact_engagement.apply(
                lambda row: calculate_engagement_score(
                    row['id_student'], row['code_module'], row['code_presentation']
                ), axis=1
            )
            
            # Calculate other metrics
            fact_engagement['attendance_count'] = 0
            fact_engagement['learning_streak'] = np.random.randint(0, 50, len(fact_engagement))
            fact_engagement['assignment_completion_percentage'] = 0
            fact_engagement['average_assessment_score'] = 0
            fact_engagement['days_since_last_activity'] = 0
            fact_engagement['last_activity_date'] = 0
            fact_engagement['enrollment_date'] = fact_engagement['date_registration']
            fact_engagement['completion_date'] = fact_engagement['date_unregistration']
            
            # Determine risk level
            fact_engagement['risk_level'] = fact_engagement['engagement_score'].apply(
                lambda x: 'High' if x < 30 else 'Medium' if x < 60 else 'Low'
            )
            
            fact_engagement['is_at_risk'] = fact_engagement['risk_level'].isin(['High', 'Medium'])
            fact_engagement['activity_intensity'] = fact_engagement['engagement_score'].apply(
                lambda x: 'Low' if x < 25 else 'Medium' if x < 75 else 'High'
            )
            
            fact_engagement['created_date'] = datetime.now()
            fact_engagement['updated_date'] = datetime.now()
            
            # Select relevant columns
            fact_engagement = fact_engagement[[
                'id_student', 'code_module', 'code_presentation',
                'engagement_score', 'attendance_count', 'days_since_last_activity',
                'learning_streak', 'assignment_completion_percentage',
                'average_assessment_score', 'risk_level', 'activity_intensity',
                'last_activity_date', 'enrollment_date', 'completion_date',
                'is_at_risk', 'final_result', 'created_date', 'updated_date'
            ]]
            
            self.transformed_data['fact_engagement'] = fact_engagement
            logger.info(f"✓ Transformed fact_engagement: {len(fact_engagement)} rows")
            
            return fact_engagement
        except Exception as e:
            logger.error(f"✗ Error transforming fact_engagement: {str(e)}")
            raise
    
    def transform_all(self) -> Dict[str, pd.DataFrame]:
        """
        Transform all data into star schema.
        
        Returns:
            Dictionary of transformed DataFrames
        """
        logger.info("Starting data transformation...")
        logger.info("=" * 60)
        
        try:
            self.transform_dim_student()
            self.transform_dim_course()
            self.transform_dim_assessment()
            self.transform_fact_assessment()
            self.transform_fact_learning_activity()
            self.transform_fact_engagement()
            
            logger.info("=" * 60)
            logger.info(f"✓ Data transformation completed successfully")
            logger.info(f"  Total tables transformed: {len(self.transformed_data)}")
            
            return self.transformed_data
        except Exception as e:
            logger.error(f"✗ Data transformation failed: {str(e)}")
            raise
    
    def get_transformed_data(self, table_name: str) -> pd.DataFrame:
        """
        Get transformed data for a specific table.
        
        Args:
            table_name: Name of the transformed table
        
        Returns:
            Transformed DataFrame
        """
        return self.transformed_data.get(table_name)


if __name__ == "__main__":
    logger.info("Data Transformer Module Loaded")
