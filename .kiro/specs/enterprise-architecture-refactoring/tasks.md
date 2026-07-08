# Implementation Plan: Enterprise Architecture Refactoring

## Overview

This implementation plan refactors the existing competitor analysis application from a script-style codebase into an enterprise-grade system with SOLID principles, dependency injection, comprehensive error handling, and proper separation of concerns. The refactoring preserves all existing functionality while improving maintainability, testability, and scalability.

## Tasks

- [-] 1. Set up enterprise project structure and configuration management
  - Create new directory structure: `config/`, `models/`, `agents/`, `services/`, `prompts/`, `utils/`, `app/`, `tests/`
  - Implement `ConfigManager` class with environment variable and JSON file loading
  - Create `AppConfig` and `PathConfig` dataclasses with typed fields
  - Implement configuration validation for API keys, paths, timeouts, and retry counts
  - Add configuration exception handling with descriptive error messages
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10_

- [ ] 2. Implement LLM client abstraction layer
  - [ ] 2.1 Create ILLMClient interface and factory
    - Define `ILLMClient` abstract base class with `chat_completion()` and `is_available()` methods
    - Implement `LLMClientFactory` with support for "zhipu" and "mock" providers
    - Add proper type hints for all parameters and return values
    - _Requirements: 2.1, 2.7, 2.8_
  
  - [~] 2.2 Implement ZhipuLLMClient with retry logic
    - Create `ZhipuLLMClient` class implementing `ILLMClient`
    - Implement exponential backoff retry mechanism (base_delay * 2^retry_attempt)
    - Add timeout handling with configurable API_TIMEOUT_SECONDS
    - Handle network errors, HTTP 5xx responses, and empty responses
    - Log all API calls with duration, token counts, and status
    - Raise `LLMException` with context after all retries exhausted
    - _Requirements: 2.2, 2.3, 2.4, 2.5, 2.6, 2.9_
  
  - [~] 2.3 Implement MockLLMClient for testing
    - Create `MockLLMClient` with configurable response scenarios
    - Support success, API error, timeout, and empty response modes
    - _Requirements: 15.1, 15.2_

- [ ] 3. Create base agent architecture
  - [~] 3.1 Implement BaseAgent abstract class
    - Define generic `BaseAgent[TInput, TOutput]` with type parameters
    - Implement `execute()` method with validation and error handling wrapper
    - Add abstract `_execute_core_logic()` for subclass implementation
    - Implement `validate_input()` and `validate_output()` methods
    - Add execution logging with timestamps, duration, and status
    - Wrap all exceptions in `AgentExecutionException` with agent context
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [~] 3.2 Define agent data models
    - Create `CompetitorInfo` dataclass with validation
    - Create `AnalysisResult` dataclass with validation
    - Create `AgentExecutionContext` dataclass for tracking execution
    - Implement validation methods for all data models
    - _Requirements: 6.1, 6.2, 6.6, 6.7, 6.8, 6.9, 6.10, 6.11_


- [ ] 4. Implement specialized agent classes
  - [~] 4.1 Implement DiscoveryAgent
    - Create `DiscoveryAgent(BaseAgent[str, List[CompetitorInfo]])` class
    - Validate keyword is non-empty and 1-100 characters
    - Execute LLM call to discover 3-10 competitors
    - Parse LLM response into `CompetitorInfo` objects
    - Validate output contains 3-10 competitors with required fields
    - _Requirements: 3.5, 3.8, 4.4_
  
  - [~] 4.2 Implement CollectorAgent
    - Create `CollectorAgent(BaseAgent[List[CompetitorInfo], pd.DataFrame])` class
    - Validate input competitor list has name and company fields
    - Execute LLM call to collect detailed data for each competitor
    - Convert results to pandas DataFrame with required columns
    - Validate row count equals input list length
    - _Requirements: 3.6, 3.9, 4.6_
  
  - [~] 4.3 Implement analysis agents (ProductAnalysisAgent, PricingAnalysisAgent, MarketAnalysisAgent)
    - Create `ProductAnalysisAgent(BaseAgent[pd.DataFrame, pd.DataFrame])` class
    - Create `PricingAnalysisAgent(BaseAgent[pd.DataFrame, Dict[str, Any]])` class
    - Create `MarketAnalysisAgent(BaseAgent[pd.DataFrame, Dict[str, Any]])` class
    - Implement validation for each agent's input and output types
    - Add LLM calls with appropriate prompts for each analysis type
    - _Requirements: 4.7, 4.8_
  
  - [~] 4.4 Implement StrategyAgent
    - Create `StrategyAgent(BaseAgent[Dict[str, Any], str])` class
    - Validate input contains product_analysis, pricing_analysis, market_analysis
    - Execute LLM call to generate strategy recommendations
    - Validate output is non-empty string with minimum 100 characters
    - _Requirements: 3.7, 3.10_

- [~] 5. Implement prompt management system
  - Create `PromptManager` class with template loading and formatting
  - Organize prompts in subdirectories: `prompts/discovery/`, `prompts/collector/`, `prompts/analysis/`, `prompts/strategy/`
  - Implement `get_prompt(agent_name, template_name, **variables)` method
  - Add variable substitution using `{variable_name}` placeholders
  - Validate templates have all required variables before formatting
  - Raise `TemplateException` for missing variables or template files
  - Support versioned templates with `_v[N]` suffix pattern
  - Optimize template loading to complete within 100ms for 10KB of templates
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_

- [ ] 6. Implement caching service
  - [~] 6.1 Create CacheService with file-based storage
    - Implement `CacheService` class with `cache_dir` and `default_ttl` configuration
    - Create `CacheEntry` dataclass with key, data, timestamp, ttl fields
    - Implement `get()` method with expiry checking
    - Implement `set()` method with TTL support
    - Add `is_expired()` method checking current_timestamp - entry_timestamp > ttl
    - _Requirements: 5.1, 5.2, 5.3_
  
  - [~] 6.2 Implement cache methods and error handling
    - Implement `get_or_compute(key, compute_fn, ttl)` pattern
    - Add `clear()` method to delete all cache entries
    - Add `cleanup_expired()` method to remove expired entries
    - Handle cache corruption with logging and graceful degradation
    - Handle disk errors with warnings instead of exceptions
    - _Requirements: 5.4, 5.5, 5.6, 5.7, 5.8, 7.6_
  
  - [ ]* 6.3 Write property tests for cache TTL behavior
    - **Property 13: Cache TTL Expiration Behavior**
    - **Validates: Requirements 5.2, 5.3**
    - Test that expired entries return cache miss and are deleted
    - Test that valid entries within TTL are returned successfully
  
  - [ ]* 6.4 Write property tests for cache consistency
    - **Property 14: Cache Get-or-Compute Consistency**
    - **Validates: Requirement 5.4**
    - Test get_or_compute returns cached value when present
    - Test get_or_compute executes function and caches on cache miss

- [~] 7. Implement logging and observability
  - Create `Logger` class with console and file output
  - Support log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
  - Implement colored console output and plain text file output
  - Add `log_agent_execution()` method with agent name, duration, status
  - Add sensitive data redaction for fields containing "key", "token", "password", "secret", "credential"
  - Log LLM API calls with duration, token counts, and status
  - Log full stack traces for exceptions at ERROR level
  - Handle file logging failures gracefully by continuing console output
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8_

- [~] 8. Implement validation utility
  - Create `Validator` class with static validation methods
  - Implement `validate_keyword()` checking non-empty after strip and max 100 characters
  - Implement `validate_price()` checking value > 0.0
  - Implement `validate_rating()` checking value in range [0.0, 5.0]
  - Implement `validate_dataframe()` checking required columns and non-empty rows
  - Add validation for input length limits (keyword: 100, company: 500, description: 1000)
  - Add input sanitization to prevent SQL injection and script injection
  - Escape HTML special characters: <, >, &, ", '
  - Raise `ValueError` with descriptive messages for validation failures
  - _Requirements: 6.12, 6.13, 6.14, 6.15, 6.16, 6.17, 6.18, 6.19, 6.20, 14.4, 14.5, 14.6, 14.7, 14.8, 14.9, 14.10, 14.11_

- [ ] 9. Implement pipeline orchestration
  - [~] 9.1 Create PipelineOrchestrator class
    - Implement agent registration system with `register_agent()` method
    - Define execution sequence: discovery → collector → product/pricing/market (parallel) → strategy
    - Implement `execute_pipeline(keyword)` method coordinating all agents
    - Add output validation between agent stages
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [~] 9.2 Implement validation and error handling
    - Validate DiscoveryAgent output: 3-5 CompetitorInfo objects
    - Validate CollectorAgent output: non-empty DataFrame with required columns
    - Validate ProductAnalysisAgent output: non-empty DataFrame
    - Validate PricingAnalysisAgent output: dict with keys (most_expensive, least_expensive, average_price)
    - Validate MarketAnalysisAgent output: dict with keys (market_leader, trends)
    - Stop execution and raise `PipelineException` on agent failure
    - Log partial results before stopping on failure
    - _Requirements: 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11_
  
  - [~] 9.3 Implement parallel agent execution
    - Use thread pool to execute product, pricing, and market analysis agents concurrently
    - Wait for all parallel agents to complete before proceeding
    - Cancel remaining agents if any parallel agent fails
    - Raise first encountered exception from parallel execution
    - _Requirements: 4.12, 4.13, 4.14_
  
  - [ ]* 9.4 Write property tests for pipeline validation
    - **Property 11: Pipeline Error Propagation and Partial Logging**
    - **Validates: Requirements 4.3, 4.4**
    - Test that agent failures stop pipeline and log partial results
    - **Property 12: Pipeline Data Flow Validation**
    - **Validates: Requirement 4.2**
    - Test that output validation occurs between agent stages

- [~] 10. Checkpoint - Ensure core infrastructure works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Implement analysis service layer
  - [~] 11.1 Create AnalysisService class
    - Initialize with `PipelineOrchestrator`, `CacheService`, and `Logger` dependencies
    - Implement `analyze_competitors(keyword, use_cache=True)` method
    - Generate cache key from keyword using "analysis:" + keyword.lower().strip()
    - Check cache first with 3600 second TTL
    - Return cached results with `cached=True` flag on cache hit
    - _Requirements: 11.1, 11.2_
  
  - [~] 11.2 Implement pipeline execution and caching
    - Execute pipeline on cache miss
    - Convert DataFrames to JSON-serializable format before caching
    - Store results in cache after successful pipeline completion
    - Return results with `cached=False` flag and execution time
    - Validate keyword is non-empty before processing
    - _Requirements: 11.3, 11.4, 11.5, 11.6_
  
  - [~] 11.3 Implement error handling for analysis service
    - Raise `ValueError` for empty or whitespace-only keywords
    - Raise `AnalysisException` with stage name on pipeline failures
    - Log cache errors and proceed without cache on read failures
    - Log cache errors and return results on write failures
    - _Requirements: 11.7, 11.8, 11.9_
  
  - [ ]* 11.4 Write property tests for analysis service
    - **Property 27: Analysis Service Cache-First Behavior**
    - **Validates: Requirements 11.1, 11.2, 11.3**
    - Test cache hit returns cached results with flag
    - Test cache miss executes pipeline and caches results
    - **Property 28: Analysis Result Completeness**
    - **Validates: Requirement 11.4**
    - Test successful analysis contains all required fields

- [ ] 12. Implement error handling and recovery
  - [~] 12.1 Create custom exception hierarchy
    - Define `ConfigurationException` for configuration errors
    - Define `LLMException` for LLM API errors
    - Define `AgentExecutionException` for agent failures
    - Define `AgentValidationException` for validation failures
    - Define `PipelineException` for orchestration errors
    - Define `ValidationException` for data validation failures
    - Define `CacheException` for cache operation errors
    - Define `TemplateException` for prompt template errors
    - Define `AnalysisException` for analysis service errors
    - Each exception should include context fields (agent_name, stage_name, etc.)
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8_
  
  - [~] 12.2 Implement error message sanitization
    - Create `sanitize_error_message()` function to remove file paths, class names, module names
    - Remove API keys, tokens, passwords from error messages
    - Provide user-friendly error messages without technical details
    - Keep detailed technical errors in logs only
    - _Requirements: 7.9, 7.10, 14.3_
  
  - [ ]* 12.3 Write unit tests for error handling
    - Test LLM API retry with exponential backoff
    - Test error wrapping and context preservation
    - Test error message sanitization
    - Test graceful degradation on cache corruption

- [~] 13. Implement security controls
  - Implement API key loading from environment variable ZHIPU_API_KEY or config file
  - Raise `ConfigurationException` if API key is not found
  - Add sensitive field detection and redaction in Logger
  - Implement input validation to block SQL keywords (SELECT, INSERT, UPDATE, DELETE, DROP)
  - Implement input validation to block script injection characters (<, >, &, ", ', null bytes)
  - Add HTML escaping for user input in display contexts
  - Enforce HTTPS for all external API calls with SSL certificate verification
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 14.13, 14.14_

- [ ] 14. Refactor Streamlit UI layer
  - [~] 14.1 Create StreamlitUI class with dependency injection
    - Inject `AnalysisService` through constructor
    - Remove all direct imports of agents, pipeline, or LLM clients
    - Remove business logic from UI layer
    - _Requirements: 12.1, 12.2, 12.3_
  
  - [~] 14.2 Implement UI rendering methods
    - Create `render()` main method to orchestrate UI
    - Create `render_input_section()` for keyword input
    - Create `render_results_section()` for displaying analysis results
    - Create `render_error()` for error message display with sanitization
    - Delegate all business operations to `AnalysisService`
    - _Requirements: 12.4, 12.5, 12.6, 12.7_
  
  - [~] 14.3 Update app entry point with dependency injection
    - Create main() function that initializes all dependencies
    - Initialize ConfigManager and load configuration
    - Initialize Logger with configured log level
    - Create LLM client using LLMClientFactory
    - Initialize CacheService, PromptManager
    - Initialize all agents with injected dependencies
    - Initialize PipelineOrchestrator and register agents
    - Initialize AnalysisService with dependencies
    - Create StreamlitUI with AnalysisService and call render()
    - _Requirements: 10.1, 10.2, 10.3, 12.8_

- [ ] 15. Migrate existing functionality to new architecture
  - [~] 15.1 Extract prompts from agent code to template files
    - Move discovery prompts to `prompts/discovery/competitor_discovery.txt`
    - Move collector prompts to `prompts/collector/data_collection.txt`
    - Move product analysis prompts to `prompts/analysis/product_analysis.txt`
    - Move pricing analysis prompts to `prompts/analysis/pricing_analysis.txt`
    - Move market analysis prompts to `prompts/analysis/market_analysis.txt`
    - Move strategy prompts to `prompts/strategy/strategy_generation.txt`
    - Replace hardcoded prompts in agents with PromptManager calls
    - _Requirements: 8.1, 8.2_
  
  - [~] 15.2 Refactor existing agent implementations
    - Update `agents/discovery.py` to inherit from BaseAgent
    - Update `agents/collector.py` to inherit from BaseAgent
    - Update `agents/product_analysis.py` to inherit from BaseAgent
    - Update `agents/pricing_analysis.py` to inherit from BaseAgent
    - Update `agents/market_analysis.py` to inherit from BaseAgent
    - Update `agents/strategy.py` to inherit from BaseAgent
    - Add validation logic to each agent
    - Inject LLMClient, Logger, PromptManager dependencies
    - _Requirements: 3.1, 3.2, 3.3, 10.1, 10.2_
  
  - [~] 15.3 Update utility modules
    - Refactor `utils/logger.py` to use new Logger class
    - Refactor `utils/cache_manager.py` to use new CacheService
    - Update `utils/report.py` to work with new AnalysisResult model
    - Ensure all utilities use dependency injection
    - _Requirements: 9.1, 9.2, 10.1_

- [~] 16. Checkpoint - Verify refactored components
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 17. Implement testing infrastructure
  - [~] 17.1 Create unit tests for core components
    - Test ConfigManager with valid/invalid configurations
    - Test LLM client retry logic and timeout handling
    - Test agent input/output validation
    - Test cache get/set/expiry operations
    - Test Validator methods for all data types
    - Target 90% line coverage and 85% branch coverage
    - _Requirements: 15.3, 15.4_
  
  - [ ]* 17.2 Write property-based tests for invariants
    - **Property 1: Configuration Validation Completeness**
    - **Validates: Requirements 1.2, 1.3, 1.5**
    - Test configuration validation with valid/invalid values
    - **Property 3: LLM Retry Guarantee with Exponential Backoff**
    - **Validates: Requirements 2.2, 2.3**
    - Test retry attempts follow exponential backoff pattern
    - **Property 17: CompetitorInfo Validation Rules**
    - **Validates: Requirement 6.1**
    - Test CompetitorInfo validation with various inputs
    - Use Hypothesis library to generate test cases
    - _Requirements: 15.5_
  
  - [ ]* 17.3 Write integration tests for pipeline execution
    - Test complete pipeline execution with MockLLMClient
    - Test nominal execution path with all agents succeeding
    - Test discovery agent failure scenario
    - Test collector agent failure scenario
    - Test analysis agent failure scenario
    - Test strategy agent failure scenario
    - Verify error propagation and partial result logging
    - _Requirements: 15.6_
  
  - [ ]* 17.4 Write integration tests for caching behavior
    - Test cache miss → compute → cache hit flow
    - Test cache expiration and cleanup
    - Test concurrent cache access scenarios
    - Verify performance improvement from caching
    - _Requirements: 15.6_

- [~] 18. Implement performance optimizations
  - Verify parallel execution of product/pricing/market analysis agents using thread pool
  - Ensure cached queries return in < 1 second
  - Ensure fresh analysis completes in < 30 seconds for 3-5 competitors
  - Add performance logging for slow operations (cache > 1s, analysis > 30s)
  - Verify parallel execution achieves 30% time reduction vs sequential
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.6, 13.7, 13.8_

- [~] 19. Add observability and monitoring
  - Implement execution metrics logging (duration, token counts, success/failure rates)
  - Add agent execution tracking with start/end timestamps
  - Log cache hit/miss rates
  - Add performance metrics for pipeline stages
  - Ensure sensitive data is never logged
  - _Requirements: 9.2, 9.3, 9.4_

- [~] 20. Create migration documentation
  - Document new architecture and design patterns
  - Create developer guide for adding new agents
  - Document configuration options and environment variables
  - Create deployment guide with security best practices
  - Document testing strategy and coverage requirements

- [~] 21. Final integration and testing
  - Run complete test suite (unit, property-based, integration)
  - Verify all requirements are met
  - Test with real Zhipu AI API
  - Verify UI works correctly with refactored backend
  - Test error handling scenarios end-to-end
  - Verify logging and caching work correctly
  - Test performance meets targets

- [~] 22. Checkpoint - Final verification
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation and allow for user feedback
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- The refactoring preserves all existing functionality while improving code quality
- Dependencies are injected through constructors following SOLID principles
- All components are loosely coupled and independently testable
- Error handling is comprehensive with meaningful messages
- Security controls protect API keys and prevent injection attacks

## Task Dependency Graph

```json
{
  "waves": [
    {
      "id": 0,
      "tasks": ["1", "2.1"]
    },
    {
      "id": 1,
      "tasks": ["2.2", "2.3", "3.1", "3.2", "5"]
    },
    {
      "id": 2,
      "tasks": ["4.1", "4.2", "4.3", "4.4", "6.1", "7", "8"]
    },
    {
      "id": 3,
      "tasks": ["6.2", "9.1", "12.1"]
    },
    {
      "id": 4,
      "tasks": ["6.3", "6.4", "9.2", "9.3", "12.2", "13"]
    },
    {
      "id": 5,
      "tasks": ["9.4", "11.1"]
    },
    {
      "id": 6,
      "tasks": ["11.2", "11.3", "14.1"]
    },
    {
      "id": 7,
      "tasks": ["11.4", "12.3", "14.2", "15.1"]
    },
    {
      "id": 8,
      "tasks": ["14.3", "15.2", "15.3"]
    },
    {
      "id": 9,
      "tasks": ["17.1", "18", "19"]
    },
    {
      "id": 10,
      "tasks": ["17.2", "17.3", "17.4", "20"]
    },
    {
      "id": 11,
      "tasks": ["21"]
    }
  ]
}
```
