"""
Database Connection Module
Handles all database connections and operations.
"""

import mysql.connector
from mysql.connector import Error, pooling, connection
from typing import Optional, List, Tuple, Dict, Any
from contextlib import contextmanager
import logging

from config import DB_CONFIG


logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Database connection manager with connection pooling.
    """
    
    _pool: Optional[pooling.MySQLConnectionPool] = None
    _instance: Optional['DatabaseConnection'] = None
    
    def __new__(cls) -> 'DatabaseConnection':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize database connection pool if not already initialized."""
        if DatabaseConnection._pool is None:
            self._initialize_pool()
    
    @staticmethod
    def _initialize_pool() -> None:
        """Initialize MySQL connection pool."""
        try:
            DatabaseConnection._pool = pooling.MySQLConnectionPool(
                pool_name="student_engagement_pool",
                pool_size=5,
                pool_reset_session=True,
                **DB_CONFIG
            )
            logger.info(f"Database connection pool created successfully for {DB_CONFIG['database']}")
        except Error as e:
            logger.error(f"Error creating connection pool: {str(e)}")
            raise
    
    @contextmanager
    def get_connection(self) -> connection.MySQLConnection:
        """
        Context manager for getting a connection from the pool.
        
        Yields:
            MySQLConnection: Database connection
        """
        conn = None
        try:
            conn = DatabaseConnection._pool.get_connection()
            yield conn
        except Error as e:
            logger.error(f"Error getting connection from pool: {str(e)}")
            if conn:
                conn.close()
            raise
        finally:
            if conn and conn.is_connected():
                conn.close()
    
    def test_connection(self) -> bool:
        """
        Test database connection.
        
        Returns:
            bool: True if connection successful
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                logger.info("Database connection test successful")
                return True
        except Error as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
    
    def execute_query(self, query: str, params: tuple = None) -> None:
        """
        Execute a query without returning results.
        
        Args:
            query: SQL query to execute
            params: Query parameters
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                cursor.close()
                logger.debug(f"Query executed successfully: {query[:100]}...")
        except Error as e:
            logger.error(f"Error executing query: {str(e)}")
            raise
    
    def fetch_query(self, query: str, params: tuple = None) -> List[Tuple]:
        """
        Execute a query and return results.
        
        Args:
            query: SQL query to execute
            params: Query parameters
        
        Returns:
            List of tuples with query results
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                results = cursor.fetchall()
                cursor.close()
                return results
        except Error as e:
            logger.error(f"Error fetching query results: {str(e)}")
            raise
    
    def insert_batch(self, query: str, data: List[Tuple], batch_size: int = 1000) -> int:
        """
        Insert data in batches.
        
        Args:
            query: INSERT query template
            data: List of tuples to insert
            batch_size: Number of rows per batch
        
        Returns:
            int: Total rows inserted
        """
        total_inserted = 0
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                for i in range(0, len(data), batch_size):
                    batch = data[i:i + batch_size]
                    cursor.executemany(query, batch)
                    conn.commit()
                    total_inserted += len(batch)
                    logger.info(f"Inserted batch: {i//batch_size + 1} ({len(batch)} rows)")
                
                cursor.close()
                logger.info(f"Total rows inserted: {total_inserted}")
                return total_inserted
        except Error as e:
            logger.error(f"Error inserting batch: {str(e)}")
            raise
    
    def get_row_count(self, table_name: str) -> int:
        """
        Get the row count for a table.
        
        Args:
            table_name: Name of the table
        
        Returns:
            int: Number of rows in the table
        """
        try:
            results = self.fetch_query(f"SELECT COUNT(*) FROM {table_name}")
            return results[0][0] if results else 0
        except Error as e:
            logger.error(f"Error getting row count for {table_name}: {str(e)}")
            return 0
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.
        
        Args:
            table_name: Name of the table
        
        Returns:
            bool: True if table exists
        """
        try:
            query = f"""
                SELECT 1 FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = '{DB_CONFIG['database']}' 
                AND TABLE_NAME = '{table_name}'
            """
            results = self.fetch_query(query)
            return len(results) > 0
        except Error as e:
            logger.error(f"Error checking if table exists: {str(e)}")
            return False
    
    def create_database(self) -> None:
        """Create the database if it doesn't exist."""
        try:
            # Create database connection without specifying database
            config = DB_CONFIG.copy()
            database = config.pop('database')
            
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.close()
            conn.close()
            logger.info(f"Database '{database}' created or already exists")
        except Error as e:
            logger.error(f"Error creating database: {str(e)}")
            raise
    
    def execute_sql_file(self, file_path: str) -> None:
        """
        Execute SQL commands from a file.
        
        Args:
            file_path: Path to SQL file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Split by semicolon and execute each statement
                statements = sql_content.split(';')
                for statement in statements:
                    statement = statement.strip()
                    if statement:
                        cursor.execute(statement)
                
                conn.commit()
                cursor.close()
                logger.info(f"SQL file executed successfully: {file_path}")
        except Error as e:
            logger.error(f"Error executing SQL file: {str(e)}")
            raise
        except FileNotFoundError:
            logger.error(f"SQL file not found: {file_path}")
            raise
    
    def drop_table(self, table_name: str) -> None:
        """
        Drop a table.
        
        Args:
            table_name: Name of the table to drop
        """
        try:
            self.execute_query(f"DROP TABLE IF EXISTS {table_name}")
            logger.info(f"Table '{table_name}' dropped successfully")
        except Error as e:
            logger.error(f"Error dropping table: {str(e)}")
            raise
    
    def truncate_table(self, table_name: str) -> None:
        """
        Truncate a table (delete all rows).
        
        Args:
            table_name: Name of the table to truncate
        """
        try:
            self.execute_query(f"TRUNCATE TABLE {table_name}")
            logger.info(f"Table '{table_name}' truncated successfully")
        except Error as e:
            logger.error(f"Error truncating table: {str(e)}")
            raise
    
    def get_table_structure(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get the structure of a table.
        
        Args:
            table_name: Name of the table
        
        Returns:
            List of dictionaries containing column information
        """
        try:
            results = self.fetch_query(f"DESCRIBE {table_name}")
            columns = []
            for row in results:
                columns.append({
                    'field': row[0],
                    'type': row[1],
                    'null': row[2],
                    'key': row[3],
                    'default': row[4],
                    'extra': row[5]
                })
            return columns
        except Error as e:
            logger.error(f"Error getting table structure: {str(e)}")
            return []
    
    def close_all_connections(self) -> None:
        """Close all connections in the pool."""
        if DatabaseConnection._pool:
            try:
                # Connection pooling doesn't have a direct close method
                # Connections are automatically returned when not in use
                logger.info("Connection pool will be closed when application exits")
            except Error as e:
                logger.error(f"Error closing connection pool: {str(e)}")


# Create global database connection instance
db_connection = DatabaseConnection()


if __name__ == "__main__":
    # Test database connection
    db = DatabaseConnection()
    if db.test_connection():
        print("✓ Database connection successful")
    else:
        print("✗ Database connection failed")
