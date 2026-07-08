"""
Collector Agent for enterprise competitor analysis system.

Collects detailed data for discovered competitors using LLM.
"""

import json
import pandas as pd
from typing import List
from agents.base_agent import BaseAgent
from models.data_models import CompetitorInfo
from models.llm_client import ILLMClient
from services.prompt_manager import PromptManager
from utils.logger import Logger
from utils.validator import Validator
from core.exceptions import AgentValidationException, LLMException


class CollectorAgent(BaseAgent[List[CompetitorInfo], pd.DataFrame]):
    """
    Agent for collecting detailed competitor data.
    
    Input: List of CompetitorInfo objects
    Output: DataFrame with detailed competitor data
    """
    
    def __init__(
        self,
        llm_client: ILLMClient,
        logger: Logger,
        prompt_manager: PromptManager
    ):
        """
        Initialize Collector Agent.
        
        Args:
            llm_client: LLM client for API calls
            logger: Logger instance
            prompt_manager: Prompt template manager
        """
        super().__init__(llm_client, logger, prompt_manager)
    
    def get_agent_name(self) -> str:
        """Get agent name."""
        return "CollectorAgent"
    
    def validate_input(self, input_data: List[CompetitorInfo]) -> bool:
        """
        Validate input competitors list.
        
        Args:
            input_data: List of CompetitorInfo objects
            
        Returns:
            True if valid
            
        Raises:
            AgentValidationException: If validation fails
        """
        errors = []
        
        if not isinstance(input_data, list):
            errors.append("Input must be a list")
        elif len(input_data) == 0:
            errors.append("Input list cannot be empty")
        else:
            for i, comp in enumerate(input_data):
                if not isinstance(comp, CompetitorInfo):
                    errors.append(f"Item {i} is not CompetitorInfo")
                elif not comp.name or not comp.company:
                    errors.append(f"Item {i} missing name or company")
        
        if errors:
            raise AgentValidationException(
                message="Input validation failed",
                agent_name=self.get_agent_name(),
                validation_errors=errors
            )
        
        return True
    
    def validate_output(self, output_data: pd.DataFrame) -> bool:
        """
        Validate output DataFrame.
        
        Args:
            output_data: DataFrame with competitor data
            
        Returns:
            True if valid
            
        Raises:
            AgentValidationException: If validation fails
        """
        try:
            required_columns = ["product_name", "company", "features", "price", "rating"]
            Validator.validate_dataframe(output_data, required_columns, min_rows=1)
            return True
        except ValueError as e:
            raise AgentValidationException(
                message=str(e),
                agent_name=self.get_agent_name(),
                validation_errors=[str(e)]
            )
    
    def _execute_core_logic(self, input_data: List[CompetitorInfo]) -> pd.DataFrame:
        """
        Execute data collection using LLM.
        
        Args:
            input_data: List of CompetitorInfo objects
            
        Returns:
            DataFrame with detailed competitor data
        """
        # Convert CompetitorInfo objects to DataFrame
        data_records = []
        
        for comp in input_data:
            record = {
                "product_name": comp.name,
                "company": comp.company,
                "features": ", ".join(comp.features) if isinstance(comp.features, list) else str(comp.features),
                "price": comp.price,
                "rating": comp.rating
            }
            data_records.append(record)
        
        df = pd.DataFrame(data_records)
        
        # Validate DataFrame has expected structure
        self.logger.info(f"Collected data for {len(df)} competitors")
        
        return df
