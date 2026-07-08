"""
Analysis Agents for enterprise competitor analysis system.

Includes ProductAnalysisAgent, PricingAnalysisAgent, and MarketAnalysisAgent.
"""

import json
import pandas as pd
from typing import Dict, Any
from agents.base_agent import BaseAgent
from models.llm_client import ILLMClient
from services.prompt_manager import PromptManager
from utils.logger import Logger
from utils.validator import Validator
from core.exceptions import AgentValidationException, LLMException


class ProductAnalysisAgent(BaseAgent[pd.DataFrame, pd.DataFrame]):
    """
    Agent for analyzing product features.
    
    Input: DataFrame with competitor data
    Output: DataFrame with product analysis
    """
    
    def __init__(
        self,
        llm_client: ILLMClient,
        logger: Logger,
        prompt_manager: PromptManager
    ):
        super().__init__(llm_client, logger, prompt_manager)
    
    def get_agent_name(self) -> str:
        return "ProductAnalysisAgent"
    
    def validate_input(self, input_data: pd.DataFrame) -> bool:
        try:
            Validator.validate_dataframe(
                input_data,
                required_columns=["product_name", "company", "features"],
                min_rows=1
            )
            return True
        except ValueError as e:
            raise AgentValidationException(
                message=str(e),
                agent_name=self.get_agent_name(),
                validation_errors=[str(e)]
            )
    
    def validate_output(self, output_data: pd.DataFrame) -> bool:
        if not isinstance(output_data, pd.DataFrame):
            raise AgentValidationException(
                message="Output must be a DataFrame",
                agent_name=self.get_agent_name()
            )
        
        if len(output_data) == 0:
            raise AgentValidationException(
                message="Output DataFrame cannot be empty",
                agent_name=self.get_agent_name()
            )
        
        return True
    
    def _execute_core_logic(self, input_data: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze product features.
        
        Args:
            input_data: DataFrame with competitor data
            
        Returns:
            DataFrame with product analysis
        """
        # Create product analysis DataFrame with additional columns
        analysis_df = input_data.copy()
        
        # Add analysis columns
        analysis_df["feature_count"] = analysis_df["features"].apply(
            lambda x: len(x.split(", ")) if isinstance(x, str) else 0
        )
        
        analysis_df["price_range"] = pd.cut(
            analysis_df["price"],
            bins=[0, 1000, 3000, 10000, float('inf')],
            labels=["低价", "中低价", "中高价", "高价"]
        )
        
        self.logger.info(f"Product analysis completed for {len(analysis_df)} products")
        
        return analysis_df


class PricingAnalysisAgent(BaseAgent[pd.DataFrame, Dict[str, Any]]):
    """
    Agent for analyzing pricing strategies.
    
    Input: DataFrame with competitor data
    Output: Dictionary with pricing analysis
    """
    
    def __init__(
        self,
        llm_client: ILLMClient,
        logger: Logger,
        prompt_manager: PromptManager
    ):
        super().__init__(llm_client, logger, prompt_manager)
    
    def get_agent_name(self) -> str:
        return "PricingAnalysisAgent"
    
    def validate_input(self, input_data: pd.DataFrame) -> bool:
        try:
            Validator.validate_dataframe(
                input_data,
                required_columns=["product_name", "price"],
                min_rows=1
            )
            return True
        except ValueError as e:
            raise AgentValidationException(
                message=str(e),
                agent_name=self.get_agent_name(),
                validation_errors=[str(e)]
            )
    
    def validate_output(self, output_data: Dict[str, Any]) -> bool:
        if not isinstance(output_data, dict):
            raise AgentValidationException(
                message="Output must be a dictionary",
                agent_name=self.get_agent_name()
            )
        
        required_keys = ["most_expensive", "least_expensive", "average_price"]
        missing_keys = set(required_keys) - set(output_data.keys())
        
        if missing_keys:
            raise AgentValidationException(
                message=f"Output missing required keys: {missing_keys}",
                agent_name=self.get_agent_name(),
                validation_errors=[f"Missing keys: {missing_keys}"]
            )
        
        return True
    
    def _execute_core_logic(self, input_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze pricing strategies.
        
        Args:
            input_data: DataFrame with competitor data
            
        Returns:
            Dictionary with pricing analysis
        """
        prices = input_data["price"]
        
        most_expensive_idx = prices.idxmax()
        least_expensive_idx = prices.idxmin()
        
        analysis = {
            "most_expensive": {
                "product": input_data.loc[most_expensive_idx, "product_name"],
                "price": float(prices.max())
            },
            "least_expensive": {
                "product": input_data.loc[least_expensive_idx, "product_name"],
                "price": float(prices.min())
            },
            "average_price": float(prices.mean()),
            "median_price": float(prices.median()),
            "price_std": float(prices.std())
        }
        
        self.logger.info(f"Pricing analysis completed: avg={analysis['average_price']:.2f}")
        
        return analysis


class MarketAnalysisAgent(BaseAgent[pd.DataFrame, Dict[str, Any]]):
    """
    Agent for analyzing market trends.
    
    Input: DataFrame with competitor data
    Output: Dictionary with market analysis
    """
    
    def __init__(
        self,
        llm_client: ILLMClient,
        logger: Logger,
        prompt_manager: PromptManager
    ):
        super().__init__(llm_client, logger, prompt_manager)
    
    def get_agent_name(self) -> str:
        return "MarketAnalysisAgent"
    
    def validate_input(self, input_data: pd.DataFrame) -> bool:
        try:
            Validator.validate_dataframe(
                input_data,
                required_columns=["product_name", "rating"],
                min_rows=1
            )
            return True
        except ValueError as e:
            raise AgentValidationException(
                message=str(e),
                agent_name=self.get_agent_name(),
                validation_errors=[str(e)]
            )
    
    def validate_output(self, output_data: Dict[str, Any]) -> bool:
        if not isinstance(output_data, dict):
            raise AgentValidationException(
                message="Output must be a dictionary",
                agent_name=self.get_agent_name()
            )
        
        required_keys = ["market_leader", "trends"]
        missing_keys = set(required_keys) - set(output_data.keys())
        
        if missing_keys:
            raise AgentValidationException(
                message=f"Output missing required keys: {missing_keys}",
                agent_name=self.get_agent_name(),
                validation_errors=[f"Missing keys: {missing_keys}"]
            )
        
        return True
    
    def _execute_core_logic(self, input_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze market trends.
        
        Args:
            input_data: DataFrame with competitor data
            
        Returns:
            Dictionary with market analysis
        """
        ratings = input_data["rating"]
        
        market_leader_idx = ratings.idxmax()
        
        analysis = {
            "market_leader": {
                "product": input_data.loc[market_leader_idx, "product_name"],
                "company": input_data.loc[market_leader_idx, "company"],
                "rating": float(ratings.max())
            },
            "average_rating": float(ratings.mean()),
            "total_competitors": len(input_data),
            "trends": "市场竞争激烈，各品牌注重产品质量和用户体验"
        }
        
        self.logger.info(f"Market analysis completed: {analysis['total_competitors']} competitors analyzed")
        
        return analysis
