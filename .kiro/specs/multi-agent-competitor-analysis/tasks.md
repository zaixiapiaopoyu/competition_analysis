# Implementation Plan: Multi-Agent Competitor Analysis System

## Overview

This implementation plan breaks down the Multi-Agent Competitor Analysis System into discrete, testable coding tasks. The system will be built in Python using Streamlit for the UI, pandas for data manipulation, and matplotlib for visualization. Each task builds incrementally toward a complete, working application with multiple specialized agents coordinated by a pipeline.

## Tasks

- [x] 1. Set up project structure and configuration
  - Create directory structure with agents/, core/, utils/ folders
  - Create config.py with API_KEY constant set to "xwjljbg"
  - Create requirements.txt with dependencies: streamlit, pandas, matplotlib, typing-extensions
  - Create empty __init__.py files in all package directories
  - _Requirements: 13.1, 13.2, 13.3_

- [x] 2. Implement mock data module
  - [x] 2.1 Create utils/data_mock.py with mock competitor database
    - Define mock data for at least 3 product categories (e.g., "手机", "笔记本电脑", "耳机")
    - Each category should have 3-5 competitors with name, company, features list, price, rating
    - Implement get_mock_competitors(keyword) function that returns category-specific data
    - Implement get_default_competitors() as fallback for unknown keywords
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_
  
  - [ ]* 2.2 Write property test for mock data validity
    - **Property 5: Data Validation - Positive Prices**
    - **Property 6: Data Validation - Rating Range**
    - Verify all mock prices are positive
    - Verify all mock ratings are in [0.0, 5.0]
    - _Requirements: 2.3, 2.4_

- [x] 3. Implement Discovery Agent
  - [x] 3.1 Create agents/discovery.py with DiscoveryAgent class
    - Implement discover_competitors(keyword: str, api_key: str) method
    - Validate API key equals "xwjljbg"
    - Validate keyword is non-empty
    - Use mock data module to fetch competitors
    - Ensure returned list has 3-5 competitors
    - Return List[Dict[str, str]] with name and company fields
    - _Requirements: 1.1, 1.2, 1.3, 3.1, 3.2_
  
  - [ ]* 3.2 Write property tests for Discovery Agent
    - **Property 1: Competitor Count Range**
    - **Property 2: Competitor Data Completeness**
    - **Property 3: Discovery Determinism**
    - **Property 8: API Key Authentication**
    - _Requirements: 1.1, 1.2, 1.5, 3.1, 3.2_
  
  - [ ]* 3.3 Write unit tests for Discovery Agent edge cases
    - Test empty keyword raises ValueError
    - Test invalid API key raises ValueError
    - Test whitespace-only keyword raises ValueError
    - _Requirements: 1.3, 3.2_


- [x] 4. Implement Collector Agent
  - [x] 4.1 Create agents/collector.py with CollectorAgent class
    - Implement collect_data(competitors: List[Dict], api_key: str) method
    - Validate API key
    - Generate mock detailed data for each competitor using data_mock utilities
    - Create pandas DataFrame with columns: product_name, company, features, price, rating
    - Ensure all prices are positive
    - Ensure all ratings are in [0.0, 5.0]
    - Ensure all feature lists are non-empty
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1_
  
  - [ ]* 4.2 Write property tests for Collector Agent
    - **Property 4: Collector Row Count Consistency**
    - **Property 5: Data Validation - Positive Prices**
    - **Property 6: Data Validation - Rating Range**
    - **Property 7: Data Validation - Non-Empty Features**
    - _Requirements: 2.1, 2.3, 2.4, 2.5_

- [x] 5. Implement Product Analysis Agent
  - [x] 5.1 Create agents/product_analysis.py with ProductAnalysisAgent class
    - Implement analyze_features(data: pd.DataFrame, api_key: str) method
    - Validate API key
    - Extract all unique features across all products
    - Create binary feature matrix (products × features)
    - Use pandas DataFrame with product names as index, features as columns
    - Set cell to 1/True if product has feature, 0/False otherwise
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_
  
  - [ ]* 5.2 Write property tests for Product Analysis Agent
    - **Property 9: Feature Matrix Dimensions**
    - **Property 10: Feature Matrix Binary Values**
    - _Requirements: 4.2, 4.3, 4.5, 4.6_

- [x] 6. Implement Pricing Analysis Agent
  - [x] 6.1 Create agents/pricing_analysis.py with PricingAnalysisAgent class
    - Implement analyze_pricing(data: pd.DataFrame, api_key: str) method
    - Validate API key
    - Find product with maximum price (most expensive)
    - Find product with minimum price (least expensive)
    - Calculate rating/price ratio for each product
    - Identify product with highest ratio (best value)
    - Calculate price range as (min, max) tuple
    - Calculate average price
    - Return dictionary with all pricing analysis results
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ]* 6.2 Write property tests for Pricing Analysis Agent
    - **Property 11: Pricing Maximum Identification**
    - **Property 12: Pricing Minimum Identification**
    - **Property 13: Best Value Calculation**
    - **Property 14: Price Range Correctness**
    - **Property 15: Average Price Calculation**
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_


- [x] 7. Implement Market Analysis Agent
  - [x] 7.1 Create agents/market_analysis.py with MarketAnalysisAgent class
    - Implement analyze_market(data: pd.DataFrame, api_key: str) method
    - Validate API key
    - Find product with highest rating (market leader)
    - Calculate average rating across all products
    - Generate list of mock trend observations (at least 2-3 trends)
    - Return dictionary with market analysis results
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [ ]* 7.2 Write property tests for Market Analysis Agent
    - **Property 16: Market Leader Identification**
    - **Property 17: Average Rating Calculation**
    - _Requirements: 6.1, 6.2, 6.4, 6.5_

- [x] 8. Implement Strategy Agent
  - [x] 8.1 Create agents/strategy.py with StrategyAgent class
    - Implement generate_strategy(product_analysis, pricing_analysis, market_analysis, api_key) method
    - Validate API key
    - Synthesize insights from all three analysis types
    - Generate actionable recommendations as markdown text
    - Include sections: feature gaps, pricing positioning, market opportunities
    - Ensure output is non-empty string
    - _Requirements: 7.1, 7.2, 7.3_
  
  - [ ]* 8.2 Write property test for Strategy Agent
    - **Property 18: Strategy Output Non-Empty**
    - _Requirements: 7.3_
  
  - [ ]* 8.3 Write unit tests for Strategy Agent
    - Test strategy references data from product analysis
    - Test strategy references data from pricing analysis
    - Test strategy references data from market analysis
    - _Requirements: 7.2_

- [x] 9. Checkpoint - Ensure all agent tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Implement Pipeline Orchestrator
  - [x] 10.1 Create core/pipeline.py with AnalysisPipeline class
    - Implement __init__(api_key: str) to initialize all agents
    - Implement execute(keyword: str) method that:
      1. Calls Discovery Agent to get competitors
      2. Calls Collector Agent to get detailed data
      3. Calls Product Analysis Agent for feature matrix
      4. Calls Pricing Analysis Agent for pricing insights
      5. Calls Market Analysis Agent for market trends
      6. Calls Strategy Agent to generate recommendations
      7. Aggregates all results into PipelineResult dictionary
    - Include error handling with descriptive messages
    - Ensure execution order is correct
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [ ]* 10.2 Write property tests for Pipeline
    - **Property 19: Pipeline Result Completeness**
    - Verify result contains all required fields
    - Verify no fields are None or empty
    - _Requirements: 8.3, 8.4_
  
  - [ ]* 10.3 Write integration tests for Pipeline
    - Test complete pipeline execution with various keywords
    - Test error propagation when agent fails
    - Test agent call order using mocks
    - _Requirements: 8.1, 8.5_


- [x] 11. Implement Report Generator
  - [x] 11.1 Create utils/report.py with ReportGenerator class
    - Implement generate_report(results: Dict) method
    - Format all analysis results into markdown text
    - Include sections: Executive Summary, Competitor Overview, Feature Comparison, Pricing Analysis, Market Analysis, Strategic Recommendations
    - Use markdown tables for tabular data
    - Ensure output is valid markdown syntax
    - Ensure output is non-empty
    - _Requirements: 9.1, 9.2, 9.3, 9.4_
  
  - [ ]* 11.2 Write property test for Report Generator
    - **Property 20: Report Generation Non-Empty**
    - Verify report is non-empty for any valid input
    - _Requirements: 9.4_
  
  - [ ]* 11.3 Write unit tests for Report Generator
    - Test report includes all required sections
    - Test markdown syntax validity
    - Test handling of various data formats
    - _Requirements: 9.2, 9.3_

- [x] 12. Implement Visualization Generator
  - [x] 12.1 Create utils/visualization.py with VisualizationGenerator class
    - Implement create_price_rating_chart(data: pd.DataFrame) method
      - Create scatter plot with price on x-axis, rating on y-axis
      - Label each point with product name
      - Add axis labels and title
      - Return matplotlib figure object
    - Implement create_feature_heatmap(feature_matrix: pd.DataFrame) method
      - Create heatmap of binary feature matrix
      - Use color coding (e.g., green=has feature, white=no feature)
      - Add product names on y-axis, features on x-axis
      - Return matplotlib figure object
    - Include error handling for empty or invalid data
    - _Requirements: 10.1, 10.2, 10.3, 10.5_
  
  - [ ]* 12.2 Write property test for Visualization Generator
    - **Property 21: Visualization Creation**
    - Verify matplotlib figures are created for valid data
    - _Requirements: 10.1, 10.2_
  
  - [ ]* 12.3 Write unit tests for Visualization Generator
    - Test chart creation with various data sizes
    - Test error handling for empty data
    - Test chart elements (labels, titles, axes)
    - _Requirements: 10.5_

- [-] 13. Checkpoint - Ensure all utility tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 14. Implement Streamlit UI
  - [x] 14.1 Create app.py with main Streamlit application
    - Import AnalysisPipeline, ReportGenerator, VisualizationGenerator
    - Import API_KEY from config
    - Display application title: "多Agent竞品分析系统"
    - Display application description
    - Create text input for product keyword with default value "手机"
    - Create submit button "开始分析"
    - _Requirements: 11.1, 11.2, 11.3, 11.4_
  
  - [x] 14.2 Implement result display logic in app.py
    - When submit button clicked:
      1. Initialize AnalysisPipeline with API_KEY
      2. Execute pipeline with keyword
      3. Generate report using ReportGenerator
      4. Create visualizations using VisualizationGenerator
    - Display results in tabs:
      - Tab 1: "竞品概览" - show data DataFrame
      - Tab 2: "功能对比" - show feature matrix and heatmap
      - Tab 3: "定价分析" - show pricing results and scatter plot
      - Tab 4: "市场分析" - show market analysis results
      - Tab 5: "战略建议" - show strategy recommendations
    - _Requirements: 11.5, 11.6_
  
  - [x] 14.3 Implement error handling in app.py
    - Wrap pipeline execution in try-except block
    - Display user-friendly error messages using st.error()
    - Log errors for debugging
    - _Requirements: 11.7, 14.1, 14.5_


- [ ] 15. Create project documentation
  - [x] 15.1 Create README.md with project overview
    - Describe the Multi-Agent Competitor Analysis System
    - List features and capabilities
    - Include installation instructions
    - Include usage instructions (how to run Streamlit app)
    - Include system requirements
    - Include architecture overview
    - Add example screenshots or usage examples
  
  - [~] 15.2 Add docstrings to all public methods
    - Ensure all agent methods have clear docstrings
    - Include parameter descriptions
    - Include return value descriptions
    - Include example usage where helpful

- [ ] 16. Final integration testing and polish
  - [ ]* 16.1 Run complete end-to-end integration test
    - Test with multiple different keywords
    - Verify all components work together
    - Verify UI displays correctly
    - Verify visualizations render properly
    - Test error scenarios
    - _Requirements: 11.5, 11.6_
  
  - [~] 16.2 Performance validation
    - Verify pipeline execution completes in under 2 seconds
    - Verify UI rendering is responsive
    - Optimize any bottlenecks if found
    - _Requirements: 8.6, 11.8_
  
  - [~] 16.3 Code quality improvements
    - Run code formatter (black) on all Python files
    - Add type hints where missing
    - Clean up any unused imports
    - Ensure consistent code style

- [~] 17. Final checkpoint - Ensure all tests pass and application runs
  - Ensure all tests pass, ask the user if questions arise.
  - Verify application can be launched with `streamlit run app.py`
  - Verify all features work as expected

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at major milestones
- Property tests validate universal correctness properties using hypothesis library
- Unit tests validate specific examples and edge cases
- Integration tests validate component interactions and end-to-end flows
- The system uses mock data only, no external API calls required
- API key is fixed to "xwjljbg" for demo purposes
- Python 3.8+ required for TypedDict support
