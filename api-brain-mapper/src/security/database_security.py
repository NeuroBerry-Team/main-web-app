from functools import wraps
from sqlalchemy import text
from flask import current_app


class DatabaseSecurity:
    """Database security utilities to prevent SQL injection"""
    
    @staticmethod
    def safe_raw_query(connection, query, params=None):
        """
        Execute raw SQL queries safely with parameter binding
        
        Args:
            connection: SQLAlchemy connection object
            query: SQL query string with named parameters
            params: Dictionary of parameter values
        
        Returns:
            Query result
        """
        try:
            if params:
                # Use SQLAlchemy's text() with bound parameters
                safe_query = text(query)
                result = connection.execute(safe_query, params)
            else:
                safe_query = text(query)
                result = connection.execute(safe_query)
            
            return result
        except Exception as e:
            current_app.logger.error(f"Database query error: {str(e)}")
            raise
    
    @staticmethod
    def validate_table_name(table_name, allowed_tables):
        """
        Validate table names to prevent injection
        
        Args:
            table_name: The table name to validate
            allowed_tables: List of allowed table names
        
        Returns:
            Validated table name
            
        Raises:
            ValueError: If table name is not allowed
        """
        if not table_name or table_name not in allowed_tables:
            raise ValueError(f"Invalid table name: {table_name}")
        return table_name
    
    @staticmethod
    def validate_column_name(column_name, allowed_columns):
        """
        Validate column names to prevent injection
        
        Args:
            column_name: The column name to validate
            allowed_columns: List of allowed column names
        
        Returns:
            Validated column name
            
        Raises:
            ValueError: If column name is not allowed
        """
        if not column_name or column_name not in allowed_columns:
            raise ValueError(f"Invalid column name: {column_name}")
        return column_name
    
    @staticmethod
    def secure_like_query(value):
        """
        Escape special characters for LIKE queries
        
        Args:
            value: String value to escape
            
        Returns:
            Escaped string safe for LIKE queries
        """
        if not isinstance(value, str):
            return str(value) if value is not None else ''
        
        # Escape SQL LIKE special characters
        escaped = value.replace('\\', '\\\\')
        escaped = escaped.replace('%', '\\%')
        escaped = escaped.replace('_', '\\_')
        
        return escaped
    
    @staticmethod
    def log_query_attempt(func):
        """
        Decorator to log database query attempts for monitoring
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                current_app.logger.info(
                    f"Database query attempt: {func.__name__}"
                )
                result = func(*args, **kwargs)
                current_app.logger.info(
                    f"Database query successful: {func.__name__}"
                )
                return result
            except Exception as e:
                current_app.logger.error(
                    f"Database query failed: {func.__name__} - {str(e)}"
                )
                raise
        return wrapper
    
    @staticmethod
    def validate_limit_offset(limit=None, offset=None, max_limit=1000):
        """
        Validate and sanitize LIMIT and OFFSET values
        
        Args:
            limit: Limit value
            offset: Offset value
            max_limit: Maximum allowed limit
            
        Returns:
            Tuple of (validated_limit, validated_offset)
        """
        validated_limit = None
        validated_offset = None
        
        if limit is not None:
            try:
                validated_limit = int(limit)
                if validated_limit < 0:
                    raise ValueError("Limit must be non-negative")
                if validated_limit > max_limit:
                    validated_limit = max_limit
            except (ValueError, TypeError):
                raise ValueError("Invalid limit value")
        
        if offset is not None:
            try:
                validated_offset = int(offset)
                if validated_offset < 0:
                    raise ValueError("Offset must be non-negative")
            except (ValueError, TypeError):
                raise ValueError("Invalid offset value")
        
        return validated_limit, validated_offset


# Allowed tables and columns for dynamic queries
    ALLOWED_TABLES = {
        'users',
        'roles',
        'inferences',
    }

ALLOWED_COLUMNS = {
    'users': ['id', 'email', 'first_name', 'last_name', 'created_at'],
    'inferences': ['id', 'userId', 'name', 'baseImageUrl', 'generatedImageUrl', 'createdOn'],
    'roles': ['id', 'name', 'description']
}
