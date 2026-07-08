"""
Validation utility for enterprise competitor analysis system.

Provides comprehensive data validation with security controls for input sanitization.
"""

import re
from typing import List
import pandas as pd
import html


class Validator:
    """
    Static validation utility class.
    
    Provides validation methods for:
    - Keywords and text input
    - Numeric values (prices, ratings)
    - DataFrames
    - Security (SQL injection, XSS prevention)
    """
    
    # SQL keywords to block
    SQL_KEYWORDS = [
        "SELECT", "INSERT", "UPDATE", "DELETE", "DROP",
        "CREATE", "ALTER", "TRUNCATE", "EXEC", "EXECUTE"
    ]
    
    # Dangerous characters for script injection
    INJECTION_CHARS = ["<", ">", "&", '"', "'", "\x00"]
    
    @staticmethod
    def validate_keyword(keyword: str) -> bool:
        """
        Validate keyword input.
        
        Args:
            keyword: Keyword string to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails
        """
        if not keyword:
            raise ValueError("Keyword cannot be empty")
        
        stripped = keyword.strip()
        
        if not stripped:
            raise ValueError("Keyword cannot be empty after stripping whitespace")
        
        if len(stripped) > 100:
            raise ValueError(f"Keyword exceeds maximum length of 100 characters (got {len(stripped)})")
        
        # Check for SQL injection
        upper_keyword = stripped.upper()
        for sql_keyword in Validator.SQL_KEYWORDS:
            if sql_keyword in upper_keyword:
                raise ValueError(f"Invalid input: contains potentially malicious characters (SQL keyword: {sql_keyword})")
        
        # Check for script injection characters
        for char in Validator.INJECTION_CHARS:
            if char in stripped:
                raise ValueError(f"Invalid input: contains potentially malicious characters ({repr(char)})")
        
        return True
    
    @staticmethod
    def validate_price(price: float) -> bool:
        """
        Validate price value.
        
        Args:
            price: Price value to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails
        """
        if not isinstance(price, (int, float)):
            raise ValueError(f"Price must be a number, got {type(price).__name__}")
        
        if price <= 0.0:
            raise ValueError(f"Price must be greater than 0, got {price}")
        
        return True
    
    @staticmethod
    def validate_rating(rating: float) -> bool:
        """
        Validate rating value.
        
        Args:
            rating: Rating value to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails
        """
        if not isinstance(rating, (int, float)):
            raise ValueError(f"Rating must be a number, got {type(rating).__name__}")
        
        if not (0.0 <= rating <= 5.0):
            raise ValueError(f"Rating must be between 0.0 and 5.0, got {rating}")
        
        return True
    
    @staticmethod
    def validate_dataframe(
        df: pd.DataFrame,
        required_columns: List[str],
        min_rows: int = 1
    ) -> bool:
        """
        Validate DataFrame structure.
        
        Args:
            df: DataFrame to validate
            required_columns: List of required column names
            min_rows: Minimum number of rows
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails
        """
        if not isinstance(df, pd.DataFrame):
            raise ValueError(f"Expected DataFrame, got {type(df).__name__}")
        
        # Check for required columns
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"DataFrame missing required columns: {missing_columns}")
        
        # Check row count
        if len(df) < min_rows:
            raise ValueError(f"DataFrame must contain at least {min_rows} row(s), got {len(df)}")
        
        return True
    
    @staticmethod
    def validate_text_length(
        text: str,
        field_name: str,
        max_length: int
    ) -> bool:
        """
        Validate text field length.
        
        Args:
            text: Text to validate
            field_name: Name of the field (for error message)
            max_length: Maximum allowed length
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails
        """
        if not isinstance(text, str):
            raise ValueError(f"{field_name} must be a string, got {type(text).__name__}")
        
        if len(text) > max_length:
            raise ValueError(f"{field_name} exceeds maximum length of {max_length} characters (got {len(text)})")
        
        return True
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """
        Sanitize text for HTML display by escaping special characters.
        
        Escapes: <, >, &, ", '
        
        Args:
            text: Text to sanitize
            
        Returns:
            HTML-safe text
        """
        return html.escape(text)
    
    @staticmethod
    def validate_company_name(company: str) -> bool:
        """
        Validate company name.
        
        Args:
            company: Company name to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails
        """
        if not company:
            raise ValueError("Company name cannot be empty")
        
        stripped = company.strip()
        
        if not stripped:
            raise ValueError("Company name cannot be empty after stripping whitespace")
        
        # Validate length
        Validator.validate_text_length(stripped, "Company name", 500)
        
        return True
    
    @staticmethod
    def validate_description(description: str) -> bool:
        """
        Validate product description.
        
        Args:
            description: Description to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails
        """
        if not description:
            raise ValueError("Description cannot be empty")
        
        # Validate length
        Validator.validate_text_length(description, "Description", 1000)
        
        return True
    
    @staticmethod
    def check_sql_injection(text: str) -> bool:
        """
        Check if text contains SQL injection patterns.
        
        Args:
            text: Text to check
            
        Returns:
            True if safe, False if suspicious
        """
        upper_text = text.upper()
        
        for keyword in Validator.SQL_KEYWORDS:
            if keyword in upper_text:
                return False
        
        return True
    
    @staticmethod
    def check_script_injection(text: str) -> bool:
        """
        Check if text contains script injection characters.
        
        Args:
            text: Text to check
            
        Returns:
            True if safe, False if suspicious
        """
        for char in Validator.INJECTION_CHARS:
            if char in text:
                return False
        
        return True
