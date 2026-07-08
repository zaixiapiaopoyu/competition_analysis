"""
Data models for enterprise competitor analysis system.

Defines typed data structures with validation for all business entities.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from core.exceptions import ValidationException


@dataclass
class CompetitorInfo:
    """
    Basic competitor information data model.
    
    Attributes:
        name: Product name
        company: Company name
        features: List of product features
        price: Product price (must be > 0)
        rating: Product rating (0.0 to 5.0)
    """
    name: str
    company: str
    features: List[str]
    price: float
    rating: float
    
    def validate(self) -> bool:
        """
        Validate competitor information.
        
        Returns:
            True if validation passes
            
        Raises:
            ValidationException: If validation fails
        """
        # Validate name
        if not self.name or not self.name.strip():
            raise ValidationException(
                "Competitor name cannot be empty",
                field_name="name"
            )
        
        # Validate company
        if not self.company or not self.company.strip():
            raise ValidationException(
                "Company name cannot be empty",
                field_name="company"
            )
        
        # Validate features
        if not self.features or len(self.features) == 0:
            raise ValidationException(
                "Features list must contain at least 1 item",
                field_name="features"
            )
        
        # Validate price
        if not isinstance(self.price, (int, float)) or self.price <= 0:
            raise ValidationException(
                "Price must be greater than 0",
                field_name="price",
                actual_value=self.price
            )
        
        # Validate rating
        if not isinstance(self.rating, (int, float)) or not (0.0 <= self.rating <= 5.0):
            raise ValidationException(
                "Rating must be between 0.0 and 5.0",
                field_name="rating",
                actual_value=self.rating
            )
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary with all fields
        """
        return {
            "name": self.name,
            "company": self.company,
            "features": self.features,
            "price": self.price,
            "rating": self.rating
        }


@dataclass
class AnalysisResult:
    """
    Complete analysis result data model.
    
    Attributes:
        keyword: Search keyword used
        timestamp: Analysis timestamp
        competitors: List of competitor information
        data: Raw competitor data DataFrame
        product_analysis: Product analysis results
        pricing_analysis: Pricing analysis results
        market_analysis: Market analysis results
        strategy: Strategic recommendations
        cached: Whether result was retrieved from cache
        execution_time: Execution time in seconds
    """
    keyword: str
    timestamp: datetime
    competitors: List[CompetitorInfo]
    data: pd.DataFrame
    product_analysis: pd.DataFrame
    pricing_analysis: Dict[str, Any]
    market_analysis: Dict[str, Any]
    strategy: str
    cached: bool = False
    execution_time: Optional[float] = None
    
    def validate(self) -> bool:
        """
        Validate analysis result completeness.
        
        Returns:
            True if validation passes
            
        Raises:
            ValidationException: If validation fails
        """
        # Validate keyword
        if not self.keyword or not self.keyword.strip():
            raise ValidationException(
                "Keyword cannot be empty",
                field_name="keyword"
            )
        
        # Validate competitors
        if self.competitors is None:
            raise ValidationException(
                "Competitors field cannot be null",
                field_name="competitors"
            )
        
        if not isinstance(self.competitors, list):
            raise ValidationException(
                "Competitors must be a list",
                field_name="competitors",
                expected_type="list",
                actual_value=type(self.competitors).__name__
            )
        
        # Validate data DataFrame
        if self.data is None:
            raise ValidationException(
                "Data field cannot be null",
                field_name="data"
            )
        
        if not isinstance(self.data, pd.DataFrame):
            raise ValidationException(
                "Data must be a DataFrame",
                field_name="data",
                expected_type="DataFrame",
                actual_value=type(self.data).__name__
            )
        
        if len(self.data) == 0:
            raise ValidationException(
                "Data DataFrame must contain at least 1 row",
                field_name="data"
            )
        
        # Validate product_analysis DataFrame
        if self.product_analysis is None:
            raise ValidationException(
                "Product analysis field cannot be null",
                field_name="product_analysis"
            )
        
        if not isinstance(self.product_analysis, pd.DataFrame):
            raise ValidationException(
                "Product analysis must be a DataFrame",
                field_name="product_analysis",
                expected_type="DataFrame",
                actual_value=type(self.product_analysis).__name__
            )
        
        if len(self.product_analysis) == 0:
            raise ValidationException(
                "Product analysis DataFrame must contain at least 1 row",
                field_name="product_analysis"
            )
        
        # Validate pricing_analysis dictionary
        if self.pricing_analysis is None:
            raise ValidationException(
                "Pricing analysis field cannot be null",
                field_name="pricing_analysis"
            )
        
        if not isinstance(self.pricing_analysis, dict):
            raise ValidationException(
                "Pricing analysis must be a dictionary",
                field_name="pricing_analysis",
                expected_type="dict",
                actual_value=type(self.pricing_analysis).__name__
            )
        
        # Validate market_analysis dictionary
        if self.market_analysis is None:
            raise ValidationException(
                "Market analysis field cannot be null",
                field_name="market_analysis"
            )
        
        if not isinstance(self.market_analysis, dict):
            raise ValidationException(
                "Market analysis must be a dictionary",
                field_name="market_analysis",
                expected_type="dict",
                actual_value=type(self.market_analysis).__name__
            )
        
        # Validate strategy
        if self.strategy is None:
            raise ValidationException(
                "Strategy field cannot be null",
                field_name="strategy"
            )
        
        if not isinstance(self.strategy, str):
            raise ValidationException(
                "Strategy must be a string",
                field_name="strategy",
                expected_type="str",
                actual_value=type(self.strategy).__name__
            )
        
        if not self.strategy.strip():
            raise ValidationException(
                "Strategy cannot be empty after stripping whitespace",
                field_name="strategy"
            )
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary with all fields (DataFrames converted to dicts)
        """
        return {
            "keyword": self.keyword,
            "timestamp": self.timestamp.isoformat(),
            "competitors": [c.to_dict() for c in self.competitors],
            "data": self.data.to_dict(orient="records"),
            "product_analysis": self.product_analysis.to_dict(orient="records"),
            "pricing_analysis": self.pricing_analysis,
            "market_analysis": self.market_analysis,
            "strategy": self.strategy,
            "cached": self.cached,
            "execution_time": self.execution_time
        }


@dataclass
class AgentExecutionContext:
    """
    Context for tracking agent execution.
    
    Attributes:
        agent_name: Name of the agent
        start_time: Execution start timestamp
        end_time: Execution end timestamp
        status: Execution status (success/failure)
        error_message: Error message if failed
        input_summary: Summary of input data
        output_summary: Summary of output data
    """
    agent_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"
    error_message: Optional[str] = None
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None
    
    def mark_success(self, output_summary: Optional[str] = None) -> None:
        """
        Mark execution as successful.
        
        Args:
            output_summary: Summary of output data
        """
        self.end_time = datetime.now()
        self.status = "success"
        self.output_summary = output_summary
    
    def mark_failure(self, error_message: str) -> None:
        """
        Mark execution as failed.
        
        Args:
            error_message: Error message
        """
        self.end_time = datetime.now()
        self.status = "failure"
        self.error_message = error_message
    
    def get_duration(self) -> Optional[float]:
        """
        Get execution duration in seconds.
        
        Returns:
            Duration in seconds, or None if not finished
        """
        if self.end_time is None:
            return None
        
        return (self.end_time - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary with all fields
        """
        return {
            "agent_name": self.agent_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "error_message": self.error_message,
            "input_summary": self.input_summary,
            "output_summary": self.output_summary,
            "duration": self.get_duration()
        }
