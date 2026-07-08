"""
Pipeline orchestration for enterprise competitor analysis system.

Coordinates execution of multiple agents in correct sequence with parallel execution support.
"""

import concurrent.futures
from typing import Dict, Any, List
from datetime import datetime
from agents.base_agent import BaseAgent
from agents.discovery_agent import DiscoveryAgent
from agents.collector_agent import CollectorAgent
from agents.analysis_agents import ProductAnalysisAgent, PricingAnalysisAgent, MarketAnalysisAgent
from agents.strategy_agent import StrategyAgent, StrategyInput
from models.data_models import CompetitorInfo
from utils.logger import Logger
from core.exceptions import PipelineException, ValidationException


class PipelineOrchestrator:
    """
    Orchestrates agent execution in defined sequence.
    
    Execution sequence:
    1. DiscoveryAgent (sequential)
    2. CollectorAgent (sequential)
    3. ProductAnalysisAgent, PricingAnalysisAgent, MarketAnalysisAgent (parallel)
    4. StrategyAgent (sequential)
    
    Features:
    - Sequential and parallel execution
    - Output validation between stages
    - Error handling and partial result logging
    - Automatic cancellation on failure
    """
    
    def __init__(
        self,
        logger: Logger,
        max_workers: int = 3
    ):
        """
        Initialize pipeline orchestrator.
        
        Args:
            logger: Logger instance
            max_workers: Maximum parallel workers for concurrent execution
        """
        self.logger = logger
        self.max_workers = max_workers
        self._agents: Dict[str, BaseAgent] = {}
    
    def register_agent(self, name: str, agent: BaseAgent) -> None:
        """
        Register an agent in the pipeline.
        
        Args:
            name: Agent identifier
            agent: Agent instance
        """
        self._agents[name] = agent
        self.logger.info(f"Registered agent: {name}")
    
    def execute_pipeline(self, keyword: str) -> Dict[str, Any]:
        """
        Execute complete analysis pipeline.
        
        Args:
            keyword: Search keyword
            
        Returns:
            Dictionary with all analysis results
            
        Raises:
            PipelineException: If any stage fails
            ValidationException: If validation fails
        """
        self.logger.info(f"Starting pipeline execution for keyword: {keyword}")
        start_time = datetime.now()
        
        results = {}
        
        try:
            # Stage 1: Discovery
            self.logger.info("Stage 1: Competitor Discovery")
            discovery_agent = self._agents.get("discovery")
            if not discovery_agent:
                raise PipelineException(
                    "DiscoveryAgent not registered",
                    stage_name="discovery"
                )
            
            competitors = discovery_agent.execute(keyword)
            
            # Validate discovery output
            if not isinstance(competitors, list) or len(competitors) < 3:
                raise ValidationException(
                    f"Discovery must return 3-10 competitors, got {len(competitors) if isinstance(competitors, list) else 0}"
                )
            
            results["competitors"] = competitors
            self.logger.info(f"Discovery completed: {len(competitors)} competitors found")
            
            # Stage 2: Data Collection
            self.logger.info("Stage 2: Data Collection")
            collector_agent = self._agents.get("collector")
            if not collector_agent:
                raise PipelineException(
                    "CollectorAgent not registered",
                    stage_name="collector"
                )
            
            data_df = collector_agent.execute(competitors)
            
            # Validate collector output
            if data_df is None or len(data_df) == 0:
                raise ValidationException("Collector returned empty DataFrame")
            
            results["data"] = data_df
            self.logger.info(f"Collection completed: {len(data_df)} records")
            
            # Stage 3: Parallel Analysis (Product, Pricing, Market)
            self.logger.info("Stage 3: Parallel Analysis")
            analysis_results = self._execute_parallel_analysis(data_df)
            
            results["product_analysis"] = analysis_results["product"]
            results["pricing_analysis"] = analysis_results["pricing"]
            results["market_analysis"] = analysis_results["market"]
            
            self.logger.info("Parallel analysis completed")
            
            # Stage 4: Strategy Generation
            self.logger.info("Stage 4: Strategy Generation")
            strategy_agent = self._agents.get("strategy")
            if not strategy_agent:
                raise PipelineException(
                    "StrategyAgent not registered",
                    stage_name="strategy"
                )
            
            strategy_input = StrategyInput(
                product_analysis=results["product_analysis"],
                pricing_analysis=results["pricing_analysis"],
                market_analysis=results["market_analysis"]
            )
            
            strategy = strategy_agent.execute(strategy_input)
            
            # Validate strategy output
            if not strategy or len(strategy.strip()) < 100:
                raise ValidationException("Strategy must be at least 100 characters")
            
            results["strategy"] = strategy
            self.logger.info("Strategy generation completed")
            
            # Calculate execution time
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            results["execution_time"] = execution_time
            
            self.logger.info(f"Pipeline completed successfully in {execution_time:.2f}s")
            
            return results
            
        except Exception as e:
            # Log partial results before failing
            self.logger.error(f"Pipeline failed at stage: {str(e)}")
            
            if results:
                self.logger.info(f"Partial results collected: {list(results.keys())}")
            
            # Wrap exception
            if isinstance(e, (PipelineException, ValidationException)):
                raise
            else:
                raise PipelineException(
                    f"Pipeline execution failed: {str(e)}",
                    original_error=e
                )
    
    def _execute_parallel_analysis(self, data_df) -> Dict[str, Any]:
        """
        Execute product, pricing, and market analysis in parallel.
        
        Args:
            data_df: DataFrame with competitor data
            
        Returns:
            Dictionary with analysis results
            
        Raises:
            PipelineException: If any analysis fails
        """
        # Get agents
        product_agent = self._agents.get("product")
        pricing_agent = self._agents.get("pricing")
        market_agent = self._agents.get("market")
        
        if not all([product_agent, pricing_agent, market_agent]):
            raise PipelineException(
                "Not all analysis agents registered",
                stage_name="parallel_analysis"
            )
        
        results = {}
        errors = []
        
        # Execute in parallel using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit tasks
            future_product = executor.submit(product_agent.execute, data_df)
            future_pricing = executor.submit(pricing_agent.execute, data_df)
            future_market = executor.submit(market_agent.execute, data_df)
            
            # Collect results
            try:
                results["product"] = future_product.result()
            except Exception as e:
                errors.append(f"Product analysis failed: {str(e)}")
                self.logger.error(f"Product analysis failed: {str(e)}")
            
            try:
                results["pricing"] = future_pricing.result()
            except Exception as e:
                errors.append(f"Pricing analysis failed: {str(e)}")
                self.logger.error(f"Pricing analysis failed: {str(e)}")
            
            try:
                results["market"] = future_market.result()
            except Exception as e:
                errors.append(f"Market analysis failed: {str(e)}")
                self.logger.error(f"Market analysis failed: {str(e)}")
        
        # Check for errors
        if errors:
            raise PipelineException(
                f"Parallel analysis failed: {'; '.join(errors)}",
                stage_name="parallel_analysis"
            )
        
        # Validate all results present
        if not all(key in results for key in ["product", "pricing", "market"]):
            missing = [k for k in ["product", "pricing", "market"] if k not in results]
            raise ValidationException(f"Missing analysis results: {missing}")
        
        return results
