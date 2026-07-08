"""
Discovery Agent for enterprise competitor analysis system.

Discovers competitor products based on keyword search using LLM.
"""

import json
from typing import List
from agents.base_agent import BaseAgent
from models.data_models import CompetitorInfo
from models.llm_client import ILLMClient
from services.prompt_manager import PromptManager
from utils.logger import Logger
from utils.validator import Validator
from core.exceptions import AgentValidationException, LLMException


class DiscoveryAgent(BaseAgent[str, List[CompetitorInfo]]):
    """
    Agent for discovering competitors based on keyword.
    
    Input: Keyword string
    Output: List of 3-10 CompetitorInfo objects
    """
    
    def __init__(
        self,
        llm_client: ILLMClient,
        logger: Logger,
        prompt_manager: PromptManager
    ):
        """
        Initialize Discovery Agent.
        
        Args:
            llm_client: LLM client for API calls
            logger: Logger instance
            prompt_manager: Prompt template manager
        """
        super().__init__(llm_client, logger, prompt_manager)
    
    def get_agent_name(self) -> str:
        """Get agent name."""
        return "DiscoveryAgent"
    
    def validate_input(self, input_data: str) -> bool:
        """
        Validate keyword input.
        
        Args:
            input_data: Keyword string
            
        Returns:
            True if valid
            
        Raises:
            AgentValidationException: If validation fails
        """
        try:
            Validator.validate_keyword(input_data)
            return True
        except ValueError as e:
            raise AgentValidationException(
                message=str(e),
                agent_name=self.get_agent_name(),
                validation_errors=[str(e)]
            )
    
    def validate_output(self, output_data: List[CompetitorInfo]) -> bool:
        """
        Validate output competitors list.
        
        Args:
            output_data: List of CompetitorInfo objects
            
        Returns:
            True if valid
            
        Raises:
            AgentValidationException: If validation fails
        """
        errors = []
        
        # Check list type
        if not isinstance(output_data, list):
            errors.append("Output must be a list")
        
        # Check list size
        elif not (3 <= len(output_data) <= 10):
            errors.append(f"Output must contain 3-10 competitors, got {len(output_data)}")
        
        else:
            # Validate each competitor
            for i, comp in enumerate(output_data):
                if not isinstance(comp, CompetitorInfo):
                    errors.append(f"Item {i} is not CompetitorInfo")
                else:
                    try:
                        comp.validate()
                    except Exception as e:
                        errors.append(f"Item {i} validation failed: {str(e)}")
        
        if errors:
            raise AgentValidationException(
                message="Output validation failed",
                agent_name=self.get_agent_name(),
                validation_errors=errors
            )
        
        return True
    
    def _execute_core_logic(self, input_data: str) -> List[CompetitorInfo]:
        """
        Execute competitor discovery using LLM.
        
        Args:
            input_data: Keyword string
            
        Returns:
            List of CompetitorInfo objects
        """
        keyword = input_data.strip()
        
        # Create prompt
        prompt = f"""你是一个数据生成专家。请为产品类别「{keyword}」生成5款真实存在的竞品数据。

请生成JSON格式的数组，每个产品包含以下字段：
{{
  "name": "产品全称",
  "company": "公司名称",
  "features": ["功能1", "功能2", "功能3", "功能4", "功能5"],
  "price": 价格数字（人民币，浮点数）,
  "rating": 评分（0-5之间的浮点数，保留1位小数）
}}

要求：
1. 必须是真实存在的知名品牌和产品
2. 价格要符合该类别的市场实际情况
3. 功能要准确反映产品特性
4. 评分要合理（一般在4.0-5.0之间）
5. 只输出JSON数组，不要其他说明文字

示例格式：
[
  {{
    "name": "iPhone 15 Pro",
    "company": "Apple",
    "features": ["5G网络", "A17芯片", "钛金属边框", "动态岛", "三摄系统"],
    "price": 7999.0,
    "rating": 4.8
  }}
]

请开始生成{keyword}类别的5款竞品数据："""
        
        # Call LLM
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self.llm_client.chat_completion(
                messages=messages,
                temperature=0.8
            )
        except LLMException as e:
            self.logger.error(f"LLM call failed in DiscoveryAgent: {str(e)}")
            raise
        
        # Parse response
        competitors = self._parse_llm_response(response)
        
        return competitors
    
    def _parse_llm_response(self, response: str) -> List[CompetitorInfo]:
        """
        Parse LLM response into CompetitorInfo objects.
        
        Args:
            response: Raw LLM response
            
        Returns:
            List of CompetitorInfo objects
            
        Raises:
            AgentValidationException: If parsing fails
        """
        try:
            # Extract JSON from response
            content = response.strip()
            
            # Handle markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            data = json.loads(content)
            
            if not isinstance(data, list):
                raise ValueError("Response is not a JSON array")
            
            # Convert to CompetitorInfo objects
            competitors = []
            for item in data[:10]:  # Take max 10
                if not isinstance(item, dict):
                    continue
                
                # Check required fields
                required_fields = ["name", "company", "features", "price", "rating"]
                if not all(field in item for field in required_fields):
                    continue
                
                # Create CompetitorInfo
                comp = CompetitorInfo(
                    name=str(item["name"]),
                    company=str(item["company"]),
                    features=item["features"] if isinstance(item["features"], list) else [],
                    price=float(item["price"]),
                    rating=float(item["rating"])
                )
                
                # Validate
                try:
                    comp.validate()
                    competitors.append(comp)
                except Exception:
                    # Skip invalid competitors
                    continue
            
            if len(competitors) < 3:
                raise ValueError(f"Only {len(competitors)} valid competitors found, need at least 3")
            
            return competitors[:10]  # Return max 10
            
        except json.JSONDecodeError as e:
            raise AgentValidationException(
                message=f"Failed to parse LLM JSON response: {str(e)}",
                agent_name=self.get_agent_name(),
                validation_errors=[f"JSON parse error: {str(e)}"]
            )
        except Exception as e:
            raise AgentValidationException(
                message=f"Failed to process LLM response: {str(e)}",
                agent_name=self.get_agent_name(),
                validation_errors=[str(e)]
            )
