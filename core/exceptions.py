"""
Custom exception hierarchy for the enterprise competitor analysis system.

This module defines all custom exceptions used throughout the application,
providing clear error messages and context for different failure scenarios.
"""

from typing import Optional, Any


class BaseApplicationException(Exception):
    """
    Base exception for all application-specific exceptions.
    
    Attributes:
        message: Human-readable error message
        context: Additional context information (dict)
    """
    
    def __init__(self, message: str, context: Optional[dict] = None):
        self.message = message
        self.context = context or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} (Context: {context_str})"
        return self.message


class ConfigurationException(BaseApplicationException):
    """
    Exception raised for configuration-related errors.
    
    Used when:
    - Required configuration values are missing
    - Configuration values fail validation
    - Configuration files cannot be read
    """
    
    def __init__(self, message: str, field_name: Optional[str] = None):
        context = {"field_name": field_name} if field_name else {}
        super().__init__(message, context)
        self.field_name = field_name


class LLMException(BaseApplicationException):
    """
    Exception raised for LLM API-related errors.
    
    Used when:
    - LLM API calls fail after all retries
    - API returns invalid responses
    - Network timeouts occur
    - API authentication fails
    """
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        retry_count: Optional[int] = None,
        original_error: Optional[Exception] = None
    ):
        context = {}
        if provider:
            context["provider"] = provider
        if retry_count is not None:
            context["retry_count"] = retry_count
        
        super().__init__(message, context)
        self.provider = provider
        self.retry_count = retry_count
        self.original_error = original_error


class AgentExecutionException(BaseApplicationException):
    """
    Exception raised when an agent fails during execution.
    
    Used when:
    - Agent execution fails due to internal errors
    - Agent cannot process input data
    - Agent dependencies are unavailable
    """
    
    def __init__(
        self,
        message: str,
        agent_name: str,
        operation: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        context = {"agent_name": agent_name}
        if operation:
            context["operation"] = operation
        
        super().__init__(message, context)
        self.agent_name = agent_name
        self.operation = operation
        self.original_error = original_error


class AgentValidationException(BaseApplicationException):
    """
    Exception raised when agent input/output validation fails.
    
    Used when:
    - Input data doesn't meet agent requirements
    - Output data doesn't match expected format
    - Required fields are missing
    """
    
    def __init__(
        self,
        message: str,
        agent_name: str,
        validation_errors: Optional[list] = None
    ):
        context = {"agent_name": agent_name}
        if validation_errors:
            context["validation_errors"] = validation_errors
        
        super().__init__(message, context)
        self.agent_name = agent_name
        self.validation_errors = validation_errors or []


class PipelineException(BaseApplicationException):
    """
    Exception raised for pipeline orchestration errors.
    
    Used when:
    - Pipeline execution fails at any stage
    - Agent dependencies cannot be resolved
    - Pipeline configuration is invalid
    """
    
    def __init__(
        self,
        message: str,
        stage_name: Optional[str] = None,
        failed_agent: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        context = {}
        if stage_name:
            context["stage_name"] = stage_name
        if failed_agent:
            context["failed_agent"] = failed_agent
        
        super().__init__(message, context)
        self.stage_name = stage_name
        self.failed_agent = failed_agent
        self.original_error = original_error


class ValidationException(BaseApplicationException):
    """
    Exception raised for data validation failures.
    
    Used when:
    - Input data fails validation rules
    - Data types don't match expected types
    - Required fields are missing or invalid
    """
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        expected_type: Optional[str] = None,
        actual_value: Optional[Any] = None
    ):
        context = {}
        if field_name:
            context["field_name"] = field_name
        if expected_type:
            context["expected_type"] = expected_type
        if actual_value is not None:
            context["actual_value"] = str(actual_value)[:100]  # Truncate long values
        
        super().__init__(message, context)
        self.field_name = field_name
        self.expected_type = expected_type
        self.actual_value = actual_value


class CacheException(BaseApplicationException):
    """
    Exception raised for cache operation errors.
    
    Used when:
    - Cache read/write operations fail
    - Cache corruption is detected
    - Cache storage is unavailable
    """
    
    def __init__(
        self,
        message: str,
        cache_key: Optional[str] = None,
        operation: Optional[str] = None
    ):
        context = {}
        if cache_key:
            context["cache_key"] = cache_key
        if operation:
            context["operation"] = operation
        
        super().__init__(message, context)
        self.cache_key = cache_key
        self.operation = operation


class TemplateException(BaseApplicationException):
    """
    Exception raised for prompt template errors.
    
    Used when:
    - Template files cannot be found
    - Template variables are missing
    - Template format is invalid
    """
    
    def __init__(
        self,
        message: str,
        template_name: Optional[str] = None,
        missing_variables: Optional[list] = None
    ):
        context = {}
        if template_name:
            context["template_name"] = template_name
        if missing_variables:
            context["missing_variables"] = missing_variables
        
        super().__init__(message, context)
        self.template_name = template_name
        self.missing_variables = missing_variables or []


class AnalysisException(BaseApplicationException):
    """
    Exception raised for analysis service errors.
    
    Used when:
    - Complete analysis workflow fails
    - Analysis results are invalid
    - Analysis cannot be completed
    """
    
    def __init__(
        self,
        message: str,
        stage_name: Optional[str] = None,
        keyword: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        context = {}
        if stage_name:
            context["stage_name"] = stage_name
        if keyword:
            context["keyword"] = keyword
        
        super().__init__(message, context)
        self.stage_name = stage_name
        self.keyword = keyword
        self.original_error = original_error
