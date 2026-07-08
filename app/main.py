"""
Main application entry point for enterprise competitor analysis system.

Initializes all dependencies with dependency injection and starts the UI.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config_manager import ConfigManager
from models.llm_client import LLMClientFactory
from services.cache_service import CacheService
from services.prompt_manager import PromptManager
from services.pipeline_orchestrator import PipelineOrchestrator
from services.analysis_service import AnalysisService
from agents.discovery_agent import DiscoveryAgent
from agents.collector_agent import CollectorAgent
from agents.analysis_agents import ProductAnalysisAgent, PricingAnalysisAgent, MarketAnalysisAgent
from agents.strategy_agent import StrategyAgent
from app.streamlit_ui import StreamlitUI
from utils.logger import Logger
from core.exceptions import ConfigurationException


def main():
    """
    Main application entry point.
    
    Initializes all dependencies and starts the application.
    """
    try:
        # Step 1: Initialize configuration
        print("🔧 Initializing configuration...")
        config_manager = ConfigManager()
        
        # Load app config
        app_config = config_manager.load_config()
        print(f"✓ Configuration loaded: model={app_config.model_name}")
        
        # Load path config
        base_dir = Path.cwd()
        path_config = config_manager.load_path_config(base_dir)
        print(f"✓ Paths configured: cache={path_config.cache_dir}")
        
        # Step 2: Initialize logger
        print("📝 Initializing logger...")
        logger = Logger(
            name="CompetitorAnalysis",
            log_level=app_config.log_level,
            log_dir=path_config.logs_dir,
            enable_console=True,
            enable_file=True
        )
        logger.info("="*70)
        logger.info("Starting Enterprise Competitor Analysis System")
        logger.info("="*70)
        
        # Step 3: Initialize LLM client
        print("🤖 Initializing LLM client...")
        llm_client = LLMClientFactory.create_client(
            provider="zhipu",
            api_key=app_config.api_key,
            model_name=app_config.model_name,
            timeout=app_config.api_timeout_seconds,
            max_retries=app_config.max_retries
        )
        logger.info(f"LLM client initialized: provider=zhipu, model={app_config.model_name}")
        
        # Step 4: Initialize services
        print("⚙️  Initializing services...")
        
        # Cache service
        cache_service = CacheService(
            cache_dir=path_config.cache_dir,
            default_ttl=app_config.cache_expiry_seconds
        )
        logger.info(f"Cache service initialized: ttl={app_config.cache_expiry_seconds}s")
        
        # Prompt manager
        prompt_manager = PromptManager(prompt_dir=path_config.prompts_dir)
        logger.info("Prompt manager initialized")
        
        # Step 5: Initialize agents
        print("🤖 Initializing agents...")
        
        # Create agents with dependency injection
        discovery_agent = DiscoveryAgent(llm_client, logger, prompt_manager)
        collector_agent = CollectorAgent(llm_client, logger, prompt_manager)
        product_agent = ProductAnalysisAgent(llm_client, logger, prompt_manager)
        pricing_agent = PricingAnalysisAgent(llm_client, logger, prompt_manager)
        market_agent = MarketAnalysisAgent(llm_client, logger, prompt_manager)
        strategy_agent = StrategyAgent(llm_client, logger, prompt_manager)
        
        logger.info("All agents initialized")
        
        # Step 6: Initialize pipeline orchestrator
        print("🔄 Initializing pipeline orchestrator...")
        orchestrator = PipelineOrchestrator(
            logger=logger,
            max_workers=app_config.max_concurrent_requests
        )
        
        # Register agents
        orchestrator.register_agent("discovery", discovery_agent)
        orchestrator.register_agent("collector", collector_agent)
        orchestrator.register_agent("product", product_agent)
        orchestrator.register_agent("pricing", pricing_agent)
        orchestrator.register_agent("market", market_agent)
        orchestrator.register_agent("strategy", strategy_agent)
        
        logger.info("Pipeline orchestrator initialized with 6 agents")
        
        # Step 7: Initialize analysis service
        print("📊 Initializing analysis service...")
        analysis_service = AnalysisService(
            pipeline_orchestrator=orchestrator,
            cache_service=cache_service,
            logger=logger
        )
        logger.info("Analysis service initialized")
        
        # Step 8: Initialize and run UI
        print("🎨 Starting user interface...")
        print("="*70)
        print("✓ System initialized successfully!")
        print("✓ Open your browser to view the application")
        print("="*70)
        
        logger.info("Starting Streamlit UI")
        
        ui = StreamlitUI(analysis_service)
        ui.render()
        
    except ConfigurationException as e:
        print(f"\n❌ Configuration Error: {e.message}")
        print(f"   Field: {e.field_name}")
        print("\n💡 Please check:")
        print("   1. ZHIPU_API_KEY environment variable is set")
        print("   2. API key is valid (32-128 characters)")
        print("   3. All required directories exist")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Fatal Error: {str(e)}")
        print("\n💡 Please check the logs for more details")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
