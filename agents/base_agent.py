"""
Base agent architecture for enterprise competitor analysis system.

Provides abstract base class for all agents with validation, error handling,
and execution tracking.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional
from datetime import datetime
from models.llm_client import ILLMClient
from services.prompt_manager import PromptManager
from utils.logger import Logger
from core.exceptions import AgentExecutionException, AgentValidationException


TInput = TypeVar('TInput')
TOutput = TypeVar('TOutput')


class BaseAgent(ABC, Generic[TInput, TOutput]):
    """
    Abstract base class for all agents.
    
    Provides:
    - Input/output validation
    - Error handling and wrapping
    - Execution logging
    - Template method pattern for agent logic
    
    Type parameters:
        TInput: Input data type
        TOutput: Output data type
    """
    
    def __init__(
        self,
        llm_client: ILLMClient,
        logger: Logger,
        prompt_manager: PromptManager
    ):
        """
        Initialize base agent.
        
        Args:
            llm_client: LLM client for API calls
            logger: Logger for execution tracking
            prompt_manager: Prompt template manager
        """
        self.llm_client = llm_client
        self.logger = logger
        self.prompt_manager = prompt_manager
    
    def execute(self, input_data: TInput) -> TOutput:
        """
        Execute agent logic with validation and error handling.
        
        This is the main entry point for agent execution.
        
        Args:
            input_data: Input data for the agent
            
        Returns:
            Processed output data
            
        Raises:
            AgentExecutionException: If execution fails
            AgentValidationException: If validation fails
        """
        agent_name = self.get_agent_name()
        start_time = datetime.now()
        
        try:
            # Log execution start
            self.logger.info(f"Agent '{agent_name}' execution started")
            
            # Validate input
            self.validate_input(input_data)
            
            # Execute core logic
            output_data = self._execute_core_logic(input_data)
            
            # Validate output
            self.validate_output(output_data)
            
            # Log success
            end_time = datetime.now()
            self.logger.log_agent_execution(
                agent_name=agent_name,
                start_time=start_time,
                end_time=end_time,
                status="success"
            )
            
            return output_data
            
        except AgentValidationException:
            # Re-raise validation exceptions
            end_time = datetime.now()
            self.logger.log_agent_execution(
                agent_name=agent_name,
                start_time=start_time,
                end_time=end_time,
                status="failure",
                error_message="Validation failed"
            )
            raise
            
        except Exception as e:
            # Wrap other exceptions
            end_time = datetime.now()
            error_msg = str(e)
            
            self.logger.log_agent_execution(
                agent_name=agent_name,
                start_time=start_time,
                end_time=end_time,
                status="failure",
                error_message=error_msg
            )
            
            raise AgentExecutionException(
                message=f"Agent execution failed: {error_msg}",
                agent_name=agent_name,
                operation="execute",
                original_error=e
            )
    
    @abstractmethod
    def _execute_core_logic(self, input_data: TInput) -> TOutput:
        """
        Execute agent-specific core logic.
        
        This method must be implemented by subclasses.
        
        Args:
            input_data: Validated input data
            
        Returns:
            Processed output data
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_data: TInput) -> bool:
        """
        Validate input data.
        
        This method must be implemented by subclasses.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid
            
        Raises:
            AgentValidationException: If validation fails
        """
        pass
    
    @abstractmethod
    def validate_output(self, output_data: TOutput) -> bool:
        """
        Validate output data.
        
        This method must be implemented by subclasses.
        
        Args:
            output_data: Output data to validate
            
        Returns:
            True if valid
            
        Raises:
            AgentValidationException: If validation fails
        """
        pass
    
    @abstractmethod
    def get_agent_name(self) -> str:
        """
        Get agent identifier.
        
        Returns:
            Agent name string
        """
        pass
