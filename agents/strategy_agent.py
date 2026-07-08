"""
Strategy Agent for enterprise competitor analysis system.

Generates strategic recommendations based on analysis results.
"""

import json
import pandas as pd
from typing import Dict, Any
from dataclasses import dataclass
from agents.base_agent import BaseAgent
from models.llm_client import ILLMClient
from services.prompt_manager import PromptManager
from utils.logger import Logger
from core.exceptions import AgentValidationException, LLMException


@dataclass
class StrategyInput:
    """
    Input data structure for StrategyAgent.
    
    Attributes:
        product_analysis: Product analysis DataFrame
        pricing_analysis: Pricing analysis dictionary
        market_analysis: Market analysis dictionary
    """
    product_analysis: pd.DataFrame
    pricing_analysis: Dict[str, Any]
    market_analysis: Dict[str, Any]


class StrategyAgent(BaseAgent[StrategyInput, str]):
    """
    Agent for generating strategic recommendations.
    
    Input: StrategyInput with all analysis results
    Output: Strategic recommendations string
    """
    
    def __init__(
        self,
        llm_client: ILLMClient,
        logger: Logger,
        prompt_manager: PromptManager
    ):
        """
        Initialize Strategy Agent.
        
        Args:
            llm_client: LLM client for API calls
            logger: Logger instance
            prompt_manager: Prompt template manager
        """
        super().__init__(llm_client, logger, prompt_manager)
    
    def get_agent_name(self) -> str:
        """Get agent name."""
        return "StrategyAgent"
    
    def validate_input(self, input_data: StrategyInput) -> bool:
        """
        Validate strategy input.
        
        Args:
            input_data: StrategyInput object
            
        Returns:
            True if valid
            
        Raises:
            AgentValidationException: If validation fails
        """
        errors = []
        
        if not isinstance(input_data, StrategyInput):
            errors.append("Input must be StrategyInput")
        else:
            if not isinstance(input_data.product_analysis, pd.DataFrame):
                errors.append("product_analysis must be DataFrame")
            elif len(input_data.product_analysis) == 0:
                errors.append("product_analysis cannot be empty")
            
            if not isinstance(input_data.pricing_analysis, dict):
                errors.append("pricing_analysis must be dict")
            
            if not isinstance(input_data.market_analysis, dict):
                errors.append("market_analysis must be dict")
        
        if errors:
            raise AgentValidationException(
                message="Input validation failed",
                agent_name=self.get_agent_name(),
                validation_errors=errors
            )
        
        return True
    
    def validate_output(self, output_data: str) -> bool:
        """
        Validate strategy output.
        
        Args:
            output_data: Strategy string
            
        Returns:
            True if valid
            
        Raises:
            AgentValidationException: If validation fails
        """
        if not isinstance(output_data, str):
            raise AgentValidationException(
                message="Output must be a string",
                agent_name=self.get_agent_name()
            )
        
        if len(output_data.strip()) < 100:
            raise AgentValidationException(
                message=f"Strategy must be at least 100 characters, got {len(output_data.strip())}",
                agent_name=self.get_agent_name()
            )
        
        return True
    
    def _execute_core_logic(self, input_data: StrategyInput) -> str:
        """
        Generate strategic recommendations using LLM.
        
        Args:
            input_data: StrategyInput with all analysis results
            
        Returns:
            Strategic recommendations string
        """
        # Prepare analysis summary
        product_count = len(input_data.product_analysis)
        avg_price = input_data.pricing_analysis.get("average_price", 0)
        market_leader = input_data.market_analysis.get("market_leader", {})
        
        # Create prompt
        prompt = f"""你是一位资深的市场战略顾问。基于以下竞品分析数据，请为企业制定详细的竞争策略。

## 产品分析
- 竞品数量: {product_count}
- 产品特性分布: 已分析

## 定价分析
- 平均价格: ¥{avg_price:.2f}
- 最高价: ¥{input_data.pricing_analysis.get('most_expensive', {}).get('price', 0):.2f} ({input_data.pricing_analysis.get('most_expensive', {}).get('product', 'N/A')})
- 最低价: ¥{input_data.pricing_analysis.get('least_expensive', {}).get('price', 0):.2f} ({input_data.pricing_analysis.get('least_expensive', {}).get('product', 'N/A')})

## 市场分析
- 市场领导者: {market_leader.get('product', 'N/A')} (评分: {market_leader.get('rating', 0)})
- 平均评分: {input_data.market_analysis.get('average_rating', 0):.1f}

请从以下几个维度提供战略建议：

1. **产品定位策略**: 如何在现有市场中找到差异化定位
2. **定价策略**: 基于竞品价格分布的定价建议
3. **功能创新方向**: 应该重点开发哪些功能来获得竞争优势
4. **市场进入策略**: 如何有效进入市场并获取初始用户
5. **竞争壁垒建设**: 如何建立长期竞争优势

请提供具体、可执行的战略建议（至少300字）："""
        
        # Call LLM
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self.llm_client.chat_completion(
                messages=messages,
                temperature=0.7
            )
        except LLMException as e:
            self.logger.error(f"LLM call failed in StrategyAgent: {str(e)}")
            # Fallback to basic strategy
            response = self._generate_fallback_strategy(input_data)
        
        self.logger.info(f"Strategy generated: {len(response)} characters")
        
        return response.strip()
    
    def _generate_fallback_strategy(self, input_data: StrategyInput) -> str:
        """
        Generate fallback strategy when LLM fails.
        
        Args:
            input_data: StrategyInput with analysis results
            
        Returns:
            Basic strategy string
        """
        avg_price = input_data.pricing_analysis.get("average_price", 0)
        market_leader = input_data.market_analysis.get("market_leader", {})
        
        strategy = f"""
# 竞品分析战略建议

## 1. 产品定位策略
基于市场分析，当前市场有 {len(input_data.product_analysis)} 个主要竞品。建议采取差异化定位策略，避免与市场领导者 {market_leader.get('product', 'N/A')} 直接竞争。

## 2. 定价策略
市场平均价格为 ¥{avg_price:.2f}，建议根据目标客户群体选择合适的价格区间：
- 高端市场：定价高于平均价格，强调品质和服务
- 大众市场：定价接近平均价格，注重性价比
- 入门市场：定价低于平均价格，快速获取市场份额

## 3. 功能创新方向
分析竞品功能特性，识别市场空白点，重点开发用户真正需要但竞品未能满足的功能。

## 4. 市场进入策略
- 选择细分市场切入
- 建立早期用户社群
- 通过口碑营销扩大影响力
- 与互补产品建立合作关系

## 5. 竞争壁垒建设
- 技术创新：持续投入研发，保持技术领先
- 用户体验：打造极致的用户体验
- 品牌建设：建立强大的品牌认知
- 生态构建：建立产品生态系统，提高用户迁移成本

建议根据企业自身资源和能力，选择最适合的战略路径，并持续优化调整。
"""
        
        return strategy.strip()
