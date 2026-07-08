"""
Analysis service for enterprise competitor analysis system.

High-level service that orchestrates complete analysis workflow with caching.
"""

from typing import Dict, Any
from datetime import datetime
from services.pipeline_orchestrator import PipelineOrchestrator
from services.cache_service import CacheService
from models.data_models import AnalysisResult, CompetitorInfo
from utils.logger import Logger
from utils.validator import Validator
from core.exceptions import AnalysisException, ValidationException


class AnalysisService:
    """
    High-level analysis service.
    
    Provides:
    - Complete competitor analysis workflow
    - Caching for repeated queries
    - Error handling and user-friendly messages
    - Result validation and formatting
    """
    
    def __init__(
        self,
        pipeline_orchestrator: PipelineOrchestrator,
        cache_service: CacheService,
        logger: Logger
    ):
        """
        Initialize analysis service.
        
        Args:
            pipeline_orchestrator: Pipeline orchestrator
            cache_service: Cache service
            logger: Logger instance
        """
        self.pipeline = pipeline_orchestrator
        self.cache = cache_service
        self.logger = logger
    
    def analyze_competitors(
        self,
        keyword: str,
        use_cache: bool = True
    ) -> AnalysisResult:
        """
        Execute complete competitor analysis.
        
        Args:
            keyword: Search keyword
            use_cache: Whether to use cache
            
        Returns:
            AnalysisResult with complete analysis
            
        Raises:
            AnalysisException: If analysis fails
            ValidationException: If keyword invalid
        """
        # Validate keyword
        if not keyword or not keyword.strip():
            raise ValidationException(
                "Keyword cannot be empty",
                field_name="keyword"
            )
        
        try:
            Validator.validate_keyword(keyword)
        except ValueError as e:
            raise ValidationException(
                str(e),
                field_name="keyword"
            )
        
        # Generate cache key
        cache_key = self._generate_cache_key(keyword)
        
        # Try cache first
        if use_cache:
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                self.logger.info(f"Cache hit for keyword: {keyword}")
                return cached_result
        
        # Cache miss - execute pipeline
        self.logger.info(f"Cache miss for keyword: {keyword}, executing pipeline")
        
        try:
            start_time = datetime.now()
            
            # Execute pipeline
            pipeline_results = self.pipeline.execute_pipeline(keyword)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Create AnalysisResult
            result = AnalysisResult(
                keyword=keyword,
                timestamp=start_time,
                competitors=pipeline_results["competitors"],
                data=pipeline_results["data"],
                product_analysis=pipeline_results["product_analysis"],
                pricing_analysis=pipeline_results["pricing_analysis"],
                market_analysis=pipeline_results["market_analysis"],
                strategy=pipeline_results["strategy"],
                cached=False,
                execution_time=execution_time
            )
            
            # Validate result
            result.validate()
            
            # Cache result
            if use_cache:
                self._save_to_cache(cache_key, result)
            
            self.logger.info(f"Analysis completed in {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            
            # Determine failure stage
            stage_name = "unknown"
            if "discovery" in str(e).lower():
                stage_name = "Discovery"
            elif "collector" in str(e).lower():
                stage_name = "Data Collection"
            elif "analysis" in str(e).lower():
                stage_name = "Analysis"
            elif "strategy" in str(e).lower():
                stage_name = "Strategy Generation"
            
            raise AnalysisException(
                f"Analysis failed at {stage_name} stage",
                stage_name=stage_name,
                keyword=keyword,
                original_error=e
            )
    
    def _generate_cache_key(self, keyword: str) -> str:
        """
        Generate cache key from keyword.
        
        Args:
            keyword: Search keyword
            
        Returns:
            Cache key string
        """
        return f"analysis:{keyword.lower().strip()}"
    
    def _get_from_cache(self, cache_key: str) -> AnalysisResult:
        """
        Get analysis result from cache.
        
        Args:
            cache_key: Cache key
            
        Returns:
            AnalysisResult or None if not found
        """
        try:
            cached_data = self.cache.get(cache_key)
            
            if cached_data is None:
                return None
            
            # Reconstruct AnalysisResult from cached data
            result = AnalysisResult(
                keyword=cached_data["keyword"],
                timestamp=datetime.fromisoformat(cached_data["timestamp"]),
                competitors=[
                    CompetitorInfo(**comp) for comp in cached_data["competitors"]
                ],
                data=cached_data["data"],
                product_analysis=cached_data["product_analysis"],
                pricing_analysis=cached_data["pricing_analysis"],
                market_analysis=cached_data["market_analysis"],
                strategy=cached_data["strategy"],
                cached=True,
                execution_time=cached_data.get("execution_time")
            )
            
            return result
            
        except Exception as e:
            self.logger.warning(f"Cache read error: {str(e)}")
            return None
    
    def _save_to_cache(self, cache_key: str, result: AnalysisResult) -> bool:
        """
        Save analysis result to cache.
        
        Args:
            cache_key: Cache key
            result: AnalysisResult to cache
            
        Returns:
            True if successful
        """
        try:
            # Convert to cacheable format
            cache_data = {
                "keyword": result.keyword,
                "timestamp": result.timestamp.isoformat(),
                "competitors": [comp.to_dict() for comp in result.competitors],
                "data": result.data.to_dict(orient="records"),
                "product_analysis": result.product_analysis.to_dict(orient="records"),
                "pricing_analysis": result.pricing_analysis,
                "market_analysis": result.market_analysis,
                "strategy": result.strategy,
                "execution_time": result.execution_time
            }
            
            # Save to cache with TTL
            success = self.cache.set(cache_key, cache_data, ttl=3600)
            
            if success:
                self.logger.info(f"Cached analysis result for key: {cache_key}")
            else:
                self.logger.warning(f"Failed to cache result for key: {cache_key}")
            
            return success
            
        except Exception as e:
            self.logger.warning(f"Cache write error: {str(e)}")
            return False
