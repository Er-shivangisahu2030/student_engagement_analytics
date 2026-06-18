"""
Analytics Module
Calculates key metrics for student engagement and learning streaks.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple
from datetime import datetime, timedelta

from config import ANALYTICS_CONFIG


logger = logging.getLogger(__name__)


class EngagementAnalytics:
    """
    Calculates analytics metrics for student engagement.
    """
    
    @staticmethod
    def calculate_engagement_score(
        activity_frequency: float,
        assessment_completion: float,
        score_performance: float
    ) -> float:
        """
        Calculate overall engagement score (0-100).
        
        Args:
            activity_frequency: Activity frequency score (0-100)
            assessment_completion: Assessment completion percentage (0-100)
            score_performance: Assessment score performance (0-100)
        
        Returns:
            Weighted engagement score
        """
        weights = ANALYTICS_CONFIG['engagement_score_weights']
        
        score = (
            activity_frequency * weights['activity_frequency'] +
            assessment_completion * weights['assessment_completion'] +
            score_performance * weights['score_performance']
        )
        
        return min(100, max(0, score))
    
    @staticmethod
    def calculate_learning_streak(activity_data: pd.DataFrame, student_id: int) -> int:
        """
        Calculate consecutive days of activity (learning streak).
        
        Args:
            activity_data: DataFrame with activity information
            student_id: Student ID
        
        Returns:
            Length of current learning streak (days)
        """
        student_activity = activity_data[activity_data['id_student'] == student_id].copy()
        
        if student_activity.empty:
            return 0
        
        # Get unique active days
        active_days = sorted(student_activity['date'].unique())
        
        if not active_days:
            return 0
        
        # Calculate consecutive streak
        max_streak = 1
        current_streak = 1
        
        for i in range(1, len(active_days)):
            if active_days[i] - active_days[i-1] == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        return max_streak
    
    @staticmethod
    def calculate_assignment_completion(assessment_data: pd.DataFrame, student_id: int, course_id: str) -> float:
        """
        Calculate assignment completion percentage.
        
        Args:
            assessment_data: DataFrame with assessment results
            student_id: Student ID
            course_id: Course ID
        
        Returns:
            Completion percentage (0-100)
        """
        course_assessments = assessment_data[
            (assessment_data['id_student'] == student_id) &
            (assessment_data['code_module'] == course_id)
        ]
        
        if course_assessments.empty:
            return 0
        
        total_assessments = len(course_assessments)
        submitted_assessments = len(course_assessments[course_assessments['is_submitted'] == True])
        
        if total_assessments == 0:
            return 0
        
        return (submitted_assessments / total_assessments) * 100
    
    @staticmethod
    def calculate_attendance_percentage(activity_data: pd.DataFrame, student_id: int, course_id: str) -> float:
        """
        Calculate attendance percentage based on activity.
        
        Args:
            activity_data: DataFrame with activity information
            student_id: Student ID
            course_id: Course ID
        
        Returns:
            Attendance percentage (0-100)
        """
        course_activity = activity_data[
            (activity_data['id_student'] == student_id) &
            (activity_data['code_module'] == course_id)
        ]
        
        if course_activity.empty:
            return 0
        
        # Count days with activity
        active_days = course_activity['date'].nunique()
        
        # Assume course is ~150 days
        course_duration = 150
        
        attendance = (active_days / course_duration) * 100
        return min(100, attendance)
    
    @staticmethod
    def calculate_days_since_last_activity(activity_data: pd.DataFrame, student_id: int) -> int:
        """
        Calculate days since last activity.
        
        Args:
            activity_data: DataFrame with activity information
            student_id: Student ID
        
        Returns:
            Number of days since last activity
        """
        student_activity = activity_data[activity_data['id_student'] == student_id]
        
        if student_activity.empty:
            return 999  # High number for inactive students
        
        last_activity_day = student_activity['date'].max()
        
        # Assume current day is ~300 (end of course)
        current_day = 300
        
        return max(0, current_day - last_activity_day)
    
    @staticmethod
    def determine_risk_level(engagement_score: float, assessment_score: float, attendance: float) -> str:
        """
        Determine student risk level.
        
        Args:
            engagement_score: Engagement score (0-100)
            assessment_score: Average assessment score (0-100)
            attendance: Attendance percentage (0-100)
        
        Returns:
            Risk level: 'Low', 'Medium', or 'High'
        """
        risk_thresholds = ANALYTICS_CONFIG['risk_thresholds']
        
        # Calculate risk score
        risk_score = (
            (100 - engagement_score) * 0.4 +
            (100 - assessment_score) * 0.4 +
            (100 - attendance) * 0.2
        )
        
        if risk_score <= 30:
            return 'Low'
        elif risk_score <= 60:
            return 'Medium'
        else:
            return 'High'
    
    @staticmethod
    def calculate_course_engagement_summary(df: pd.DataFrame, course_id: str) -> Dict:
        """
        Calculate engagement metrics for a course.
        
        Args:
            df: DataFrame with engagement data
            course_id: Course ID
        
        Returns:
            Dictionary of course engagement metrics
        """
        course_data = df[df['code_module'] == course_id]
        
        if course_data.empty:
            return {}
        
        return {
            'course_id': course_id,
            'total_students': len(course_data),
            'avg_engagement_score': course_data['engagement_score'].mean(),
            'avg_completion_percentage': course_data['assignment_completion_percentage'].mean(),
            'avg_attendance': course_data['attendance_count'].mean(),
            'at_risk_count': len(course_data[course_data['is_at_risk'] == True]),
            'at_risk_percentage': (len(course_data[course_data['is_at_risk'] == True]) / len(course_data)) * 100,
        }
    
    @staticmethod
    def get_at_risk_students(df: pd.DataFrame) -> pd.DataFrame:
        """
        Get all at-risk students.
        
        Args:
            df: DataFrame with engagement data
        
        Returns:
            DataFrame of at-risk students
        """
        at_risk = df[df['is_at_risk'] == True].copy()
        at_risk = at_risk.sort_values('engagement_score', ascending=True)
        return at_risk


class EngagementTrends:
    """
    Analyzes engagement trends and patterns.
    """
    
    @staticmethod
    def get_engagement_distribution(df: pd.DataFrame) -> Dict:
        """
        Get distribution of engagement scores.
        
        Args:
            df: DataFrame with engagement data
        
        Returns:
            Dictionary of engagement distribution
        """
        return {
            'high_engagement': len(df[df['engagement_score'] >= 70]),
            'medium_engagement': len(df[(df['engagement_score'] >= 40) & (df['engagement_score'] < 70)]),
            'low_engagement': len(df[df['engagement_score'] < 40]),
        }
    
    @staticmethod
    def get_regional_statistics(df: pd.DataFrame) -> pd.DataFrame:
        """
        Get engagement statistics by region.
        
        Args:
            df: DataFrame with engagement data and region information
        
        Returns:
            DataFrame of regional statistics
        """
        if 'region' not in df.columns:
            return pd.DataFrame()
        
        regional_stats = df.groupby('region').agg({
            'engagement_score': 'mean',
            'assignment_completion_percentage': 'mean',
            'is_at_risk': 'sum'
        }).round(2)
        
        return regional_stats
    
    @staticmethod
    def get_top_performers(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
        """
        Get top performing students.
        
        Args:
            df: DataFrame with engagement data
            n: Number of top performers to return
        
        Returns:
            DataFrame of top performers
        """
        return df.nlargest(n, 'engagement_score')[
            ['id_student', 'code_module', 'engagement_score', 
             'assignment_completion_percentage', 'average_assessment_score']
        ]
    
    @staticmethod
    def get_struggling_students(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
        """
        Get struggling students who need support.
        
        Args:
            df: DataFrame with engagement data
            n: Number of struggling students to return
        
        Returns:
            DataFrame of struggling students
        """
        return df.nsmallest(n, 'engagement_score')[
            ['id_student', 'code_module', 'engagement_score',
             'assignment_completion_percentage', 'average_assessment_score',
             'risk_level']
        ]


if __name__ == "__main__":
    logger.info("Analytics Module Loaded")
