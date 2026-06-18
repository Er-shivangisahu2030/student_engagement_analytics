"""
Streamlit Dashboard
Interactive analytics dashboard for Student Engagement & Learning Streak Analytics.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database.connection import db_connection
from analytics.metrics import EngagementAnalytics, EngagementTrends


# Configure page
st.set_page_config(
    page_title="Student Engagement Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .header {
        background-color: #1f77b4;
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load data from database."""
    try:
        # Load main engagement table
        query = """
            SELECT * FROM fact_engagement 
            JOIN dim_student ON fact_engagement.student_key = dim_student.student_key
            JOIN dim_course ON fact_engagement.course_key = dim_course.course_key
            LIMIT 10000
        """
        results = db_connection.fetch_query(query)
        
        if not results:
            return None
        
        # Convert to DataFrame (simplified for demo)
        return pd.DataFrame(results)
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None


def display_header():
    """Display header section."""
    st.markdown("""
    <div class="header">
        <h1>📊 Student Engagement & Learning Streak Analytics</h1>
        <p>Real-time analytics for student learning patterns and engagement monitoring</p>
    </div>
    """, unsafe_allow_html=True)


def display_kpi_cards(data):
    """Display KPI cards."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Students",
            int(data['id_student'].nunique()),
            delta="Enrolled" if data['id_student'].nunique() > 0 else None
        )
    
    with col2:
        avg_engagement = data['engagement_score'].mean()
        st.metric(
            "Avg Engagement Score",
            f"{avg_engagement:.1f}/100",
            delta=f"{avg_engagement-50:.1f}" if avg_engagement > 50 else None
        )
    
    with col3:
        at_risk_count = len(data[data['is_at_risk'] == 1])
        at_risk_pct = (at_risk_count / len(data) * 100) if len(data) > 0 else 0
        st.metric(
            "At-Risk Students",
            at_risk_count,
            delta=f"{at_risk_pct:.1f}%"
        )
    
    with col4:
        avg_completion = data['assignment_completion_percentage'].mean()
        st.metric(
            "Avg Completion %",
            f"{avg_completion:.1f}%",
            delta=f"{avg_completion-50:.1f}%" if avg_completion > 50 else None
        )


def display_filters(data):
    """Display filter options."""
    st.sidebar.markdown("### 🔍 Filters")
    
    # Student search
    student_search = st.sidebar.text_input("Search Student ID:", "")
    
    # Course filter
    if 'code_module' in data.columns:
        courses = data['code_module'].unique()
        selected_courses = st.sidebar.multiselect(
            "Select Courses:",
            courses,
            default=courses[:3] if len(courses) > 0 else []
        )
    else:
        selected_courses = []
    
    # Risk level filter
    risk_levels = ['Low', 'Medium', 'High']
    selected_risk = st.sidebar.multiselect(
        "Select Risk Levels:",
        risk_levels,
        default=['Medium', 'High']
    )
    
    # Engagement score filter
    engagement_range = st.sidebar.slider(
        "Engagement Score Range:",
        0, 100, (0, 100)
    )
    
    return student_search, selected_courses, selected_risk, engagement_range


def filter_data(data, student_search, selected_courses, selected_risk, engagement_range):
    """Apply filters to data."""
    filtered_data = data.copy()
    
    if student_search:
        filtered_data = filtered_data[
            filtered_data['id_student'].astype(str).str.contains(student_search, na=False)
        ]
    
    if selected_courses:
        filtered_data = filtered_data[filtered_data['code_module'].isin(selected_courses)]
    
    if selected_risk:
        filtered_data = filtered_data[filtered_data['risk_level'].isin(selected_risk)]
    
    filtered_data = filtered_data[
        (filtered_data['engagement_score'] >= engagement_range[0]) &
        (filtered_data['engagement_score'] <= engagement_range[1])
    ]
    
    return filtered_data


def display_engagement_dashboard(data):
    """Display main engagement dashboard."""
    st.header("📈 Engagement Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Engagement distribution pie chart
        st.subheader("Engagement Distribution")
        engagement_dist = {
            'High (70+)': len(data[data['engagement_score'] >= 70]),
            'Medium (40-70)': len(data[(data['engagement_score'] >= 40) & (data['engagement_score'] < 70)]),
            'Low (<40)': len(data[data['engagement_score'] < 40])
        }
        
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = ['#2ecc71', '#f39c12', '#e74c3c']
        ax.pie(engagement_dist.values(), labels=engagement_dist.keys(), autopct='%1.1f%%', colors=colors)
        ax.set_title('Student Engagement Distribution')
        st.pyplot(fig)
    
    with col2:
        # Risk level distribution
        st.subheader("Risk Level Distribution")
        if 'risk_level' in data.columns:
            risk_dist = data['risk_level'].value_counts()
            
            fig, ax = plt.subplots(figsize=(8, 6))
            colors_risk = {'Low': '#2ecc71', 'Medium': '#f39c12', 'High': '#e74c3c'}
            risk_colors = [colors_risk.get(level, '#95a5a6') for level in risk_dist.index]
            ax.bar(risk_dist.index, risk_dist.values, color=risk_colors)
            ax.set_title('Students by Risk Level')
            ax.set_ylabel('Number of Students')
            st.pyplot(fig)


def display_learning_streaks(data):
    """Display learning streaks analysis."""
    st.header("🔥 Learning Streaks")
    
    if 'learning_streak' in data.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Streak Distribution")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(data['learning_streak'].dropna(), bins=30, color='#3498db', edgecolor='black')
            ax.set_xlabel('Days in Streak')
            ax.set_ylabel('Number of Students')
            ax.set_title('Distribution of Learning Streaks')
            st.pyplot(fig)
        
        with col2:
            st.subheader("Top Learning Streaks")
            top_streaks = data.nlargest(10, 'learning_streak')[
                ['id_student', 'code_module', 'learning_streak', 'engagement_score']
            ]
            st.dataframe(top_streaks, use_container_width=True)


def display_assignment_completion(data):
    """Display assignment completion analysis."""
    st.header("✅ Assignment Completion")
    
    if 'assignment_completion_percentage' in data.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Completion Rate Distribution")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(data['assignment_completion_percentage'].dropna(), bins=20, color='#9b59b6', edgecolor='black')
            ax.set_xlabel('Completion Percentage (%)')
            ax.set_ylabel('Number of Students')
            ax.set_title('Distribution of Assignment Completion Rates')
            st.pyplot(fig)
        
        with col2:
            st.subheader("Completion vs Engagement")
            fig, ax = plt.subplots(figsize=(10, 6))
            scatter = ax.scatter(
                data['assignment_completion_percentage'],
                data['engagement_score'],
                alpha=0.6,
                c=data['average_assessment_score'],
                cmap='viridis'
            )
            ax.set_xlabel('Assignment Completion %')
            ax.set_ylabel('Engagement Score')
            ax.set_title('Assignment Completion vs Engagement Score')
            plt.colorbar(scatter, ax=ax, label='Avg Assessment Score')
            st.pyplot(fig)


def display_at_risk_analysis(data):
    """Display at-risk students analysis."""
    st.header("⚠️ At-Risk Students Analysis")
    
    at_risk_students = data[data['is_at_risk'] == 1].copy()
    
    if len(at_risk_students) > 0:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("At-Risk Students Details")
            
            # Display at-risk students table
            display_cols = ['id_student', 'code_module', 'engagement_score', 
                          'assignment_completion_percentage', 'risk_level']
            available_cols = [col for col in display_cols if col in at_risk_students.columns]
            
            st.dataframe(
                at_risk_students[available_cols].head(20),
                use_container_width=True
            )
        
        with col2:
            st.subheader("Risk Breakdown")
            if 'risk_level' in at_risk_students.columns:
                risk_counts = at_risk_students['risk_level'].value_counts()
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.barh(risk_counts.index, risk_counts.values, color=['#e74c3c', '#f39c12'])
                ax.set_xlabel('Count')
                ax.set_title('At-Risk Students by Risk Level')
                st.pyplot(fig)
    else:
        st.success("✓ No at-risk students identified!")


def display_course_analytics(data):
    """Display course-level analytics."""
    st.header("📚 Course Analytics")
    
    if 'code_module' in data.columns:
        courses = data['code_module'].unique()
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            selected_course = st.selectbox("Select Course:", courses)
        
        with col2:
            st.write("")  # Spacing
        
        course_data = data[data['code_module'] == selected_course]
        
        # Display course metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Students", len(course_data))
        
        with col2:
            st.metric("Avg Engagement", f"{course_data['engagement_score'].mean():.1f}")
        
        with col3:
            st.metric("Avg Completion %", f"{course_data['assignment_completion_percentage'].mean():.1f}")
        
        with col4:
            at_risk_count = len(course_data[course_data['is_at_risk'] == 1])
            st.metric("At-Risk Count", at_risk_count)
        
        # Course engagement trends
        st.subheader(f"Engagement Metrics for {selected_course}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(course_data['engagement_score'].dropna(), bins=20, color='#3498db', edgecolor='black')
            ax.set_xlabel('Engagement Score')
            ax.set_ylabel('Number of Students')
            ax.set_title(f'Engagement Distribution - {selected_course}')
            st.pyplot(fig)
        
        with col2:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(course_data['assignment_completion_percentage'].dropna(), bins=20, color='#2ecc71', edgecolor='black')
            ax.set_xlabel('Completion %')
            ax.set_ylabel('Number of Students')
            ax.set_title(f'Assignment Completion - {selected_course}')
            st.pyplot(fig)


def display_data_quality_report():
    """Display data quality report."""
    st.header("📋 Data Quality Report")
    
    try:
        # Fetch data quality metrics from database
        query = """
            SELECT * FROM data_quality_report 
            ORDER BY created_date DESC 
            LIMIT 10
        """
        results = db_connection.fetch_query(query)
        
        if results:
            # Create DataFrame from results
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not load data quality report: {str(e)}")


def display_pipeline_status():
    """Display ETL pipeline status."""
    st.header("⚙️ Pipeline Status")
    
    try:
        # Fetch latest pipeline execution
        query = """
            SELECT * FROM pipeline_execution_log 
            ORDER BY created_date DESC 
            LIMIT 1
        """
        results = db_connection.fetch_query(query)
        
        if results:
            execution = results[0]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Status", execution[3])  # execution_status
            
            with col2:
                st.metric("Rows Extracted", f"{execution[5]:,}")  # total_rows_extracted
            
            with col3:
                st.metric("Rows Loaded", f"{execution[7]:,}")  # total_rows_loaded
            
            with col4:
                st.metric("Duration (sec)", f"{execution[9]:.2f}")  # execution_duration_seconds
        else:
            st.info("No pipeline executions found")
    except Exception as e:
        st.warning(f"Could not load pipeline status: {str(e)}")


def main():
    """Main dashboard function."""
    # Display header
    display_header()
    
    # Create sidebar
    st.sidebar.markdown("## 📊 Student Engagement Analytics")
    st.sidebar.markdown("---")
    
    # Load data
    data = load_data()
    
    if data is None or data.empty:
        st.error("❌ Could not load data. Please check database connection.")
        st.info("Make sure the ETL pipeline has been executed and data is loaded in the database.")
        return
    
    # Display filters
    student_search, selected_courses, selected_risk, engagement_range = display_filters(data)
    
    # Apply filters
    filtered_data = filter_data(data, student_search, selected_courses, selected_risk, engagement_range)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Filtered Records:** {len(filtered_data)}")
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Dashboard",
        "🔥 Learning Streaks",
        "✅ Assignments",
        "⚠️ At-Risk",
        "📚 Courses",
        "⚙️ System"
    ])
    
    with tab1:
        display_kpi_cards(filtered_data)
        display_engagement_dashboard(filtered_data)
    
    with tab2:
        display_learning_streaks(filtered_data)
    
    with tab3:
        display_assignment_completion(filtered_data)
    
    with tab4:
        display_at_risk_analysis(filtered_data)
    
    with tab5:
        display_course_analytics(filtered_data)
    
    with tab6:
        col1, col2 = st.columns(2)
        with col1:
            display_data_quality_report()
        with col2:
            display_pipeline_status()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📄 Export Data")
    if st.sidebar.button("📥 Download Filtered Data as CSV"):
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="Click here to download",
            data=csv,
            file_name=f"engagement_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("Built with ❤️ using Streamlit")


if __name__ == "__main__":
    main()
