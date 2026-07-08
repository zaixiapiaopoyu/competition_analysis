"""
Streamlit UI for enterprise competitor analysis system.

Presentation layer completely separated from business logic.
"""

import streamlit as st
import pandas as pd
from typing import Optional
from services.analysis_service import AnalysisService
from models.data_models import AnalysisResult
from utils.validator import Validator
from core.exceptions import (
    AnalysisException,
    ValidationException,
    LLMException,
    ConfigurationException
)


class StreamlitUI:
    """
    Streamlit-based user interface.
    
    Features:
    - Clean separation from business logic
    - User-friendly error messages
    - Progress indicators
    - Result visualization
    """
    
    def __init__(self, analysis_service: AnalysisService):
        """
        Initialize Streamlit UI.
        
        Args:
            analysis_service: Analysis service for business operations
        """
        self.analysis_service = analysis_service
    
    def render(self) -> None:
        """
        Main render method - orchestrates UI.
        """
        # Page configuration
        st.set_page_config(
            page_title="竞品分析系统 - Enterprise Edition",
            page_icon="🔍",
            layout="wide"
        )
        
        # Header
        self._render_header()
        
        # Input section
        keyword = self._render_input_section()
        
        # Analysis execution
        if keyword:
            self._handle_analysis_request(keyword)
    
    def _render_header(self) -> None:
        """Render page header."""
        st.title("🔍 竞品分析系统")
        st.markdown("**Enterprise Edition** - 基于多Agent架构的智能竞品分析平台")
        st.markdown("---")
    
    def _render_input_section(self) -> Optional[str]:
        """
        Render input section.
        
        Returns:
            Keyword if submitted, None otherwise
        """
        st.subheader("📝 输入分析关键词")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            keyword = st.text_input(
                "请输入产品类别或关键词",
                placeholder="例如：智能手机、笔记本电脑、无线耳机",
                help="输入您想要分析的产品类别，系统将自动发现并分析相关竞品"
            )
        
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            analyze_button = st.button("🚀 开始分析", type="primary", use_container_width=True)
        
        if analyze_button and keyword:
            return keyword.strip()
        
        return None
    
    def _handle_analysis_request(self, keyword: str) -> None:
        """
        Handle analysis request.
        
        Args:
            keyword: Search keyword
        """
        try:
            # Show progress
            with st.spinner("🔄 正在分析中，请稍候..."):
                # Execute analysis
                result = self.analysis_service.analyze_competitors(keyword, use_cache=True)
            
            # Display success message
            if result.cached:
                st.success(f"✅ 分析完成！（使用缓存数据）")
            else:
                st.success(f"✅ 分析完成！耗时 {result.execution_time:.2f} 秒")
            
            # Display results
            self._render_results_section(result)
            
        except ValidationException as e:
            self._render_error(f"输入验证失败: {e.message}")
        
        except LLMException as e:
            self._render_error("AI 服务暂时不可用，请稍后重试")
        
        except AnalysisException as e:
            stage_msg = f"在 {e.stage_name} 阶段" if e.stage_name else ""
            self._render_error(f"分析失败{stage_msg}，请重试或更换关键词")
        
        except ConfigurationException as e:
            self._render_error("系统配置错误，请联系管理员")
        
        except Exception as e:
            self._render_error("系统错误，请稍后重试")
    
    def _render_results_section(self, result: AnalysisResult) -> None:
        """
        Render analysis results.
        
        Args:
            result: Analysis result
        """
        st.markdown("---")
        st.subheader("📊 分析结果")
        
        # Create tabs for different sections
        tabs = st.tabs([
            "🎯 竞品列表",
            "📈 产品分析",
            "💰 定价分析",
            "🌍 市场分析",
            "🎯 战略建议"
        ])
        
        # Tab 1: Competitor List
        with tabs[0]:
            self._render_competitor_list(result)
        
        # Tab 2: Product Analysis
        with tabs[1]:
            self._render_product_analysis(result)
        
        # Tab 3: Pricing Analysis
        with tabs[2]:
            self._render_pricing_analysis(result)
        
        # Tab 4: Market Analysis
        with tabs[3]:
            self._render_market_analysis(result)
        
        # Tab 5: Strategy
        with tabs[4]:
            self._render_strategy(result)
    
    def _render_competitor_list(self, result: AnalysisResult) -> None:
        """Render competitor list."""
        st.write(f"发现 **{len(result.competitors)}** 个竞品：")
        
        # Display as DataFrame
        df = result.data.copy()
        st.dataframe(df, use_container_width=True)
    
    def _render_product_analysis(self, result: AnalysisResult) -> None:
        """Render product analysis."""
        st.write("### 产品特性分析")
        
        # Display product analysis DataFrame
        df = result.product_analysis.copy()
        st.dataframe(df, use_container_width=True)
        
        # Statistics
        if "feature_count" in df.columns:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("平均功能数", f"{df['feature_count'].mean():.1f}")
            
            with col2:
                st.metric("最多功能", f"{df['feature_count'].max()}")
            
            with col3:
                st.metric("最少功能", f"{df['feature_count'].min()}")
    
    def _render_pricing_analysis(self, result: AnalysisResult) -> None:
        """Render pricing analysis."""
        st.write("### 定价策略分析")
        
        pricing = result.pricing_analysis
        
        # Display key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "平均价格",
                f"¥{pricing['average_price']:.2f}"
            )
        
        with col2:
            most_exp = pricing.get('most_expensive', {})
            st.metric(
                "最高价",
                f"¥{most_exp.get('price', 0):.2f}",
                delta=most_exp.get('product', 'N/A')
            )
        
        with col3:
            least_exp = pricing.get('least_expensive', {})
            st.metric(
                "最低价",
                f"¥{least_exp.get('price', 0):.2f}",
                delta=least_exp.get('product', 'N/A')
            )
        
        # Price distribution chart
        if not result.data.empty:
            st.write("### 价格分布")
            st.bar_chart(result.data.set_index('product_name')['price'])
    
    def _render_market_analysis(self, result: AnalysisResult) -> None:
        """Render market analysis."""
        st.write("### 市场格局分析")
        
        market = result.market_analysis
        
        # Market leader
        leader = market.get('market_leader', {})
        if leader:
            st.info(f"**市场领导者**: {leader.get('product', 'N/A')} "
                   f"({leader.get('company', 'N/A')}) - "
                   f"评分: {leader.get('rating', 0):.1f} ⭐")
        
        # Market statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("平均评分", f"{market.get('average_rating', 0):.1f} ⭐")
        
        with col2:
            st.metric("竞品数量", market.get('total_competitors', 0))
        
        # Trends
        if 'trends' in market:
            st.write("### 市场趋势")
            st.write(market['trends'])
    
    def _render_strategy(self, result: AnalysisResult) -> None:
        """Render strategic recommendations."""
        st.write("### 战略建议")
        
        # Display strategy text
        st.markdown(result.strategy)
        
        # Download button
        st.download_button(
            label="📥 下载完整报告",
            data=result.strategy,
            file_name=f"strategy_{result.keyword}_{result.timestamp.strftime('%Y%m%d')}.md",
            mime="text/markdown"
        )
    
    def _render_error(self, message: str) -> None:
        """
        Render user-friendly error message.
        
        Args:
            message: Error message (already sanitized)
        """
        st.error(f"❌ {message}")
        
        # Help message
        with st.expander("💡 遇到问题？"):
            st.write("""
            **常见问题解决方案：**
            
            1. **输入验证失败**: 请确保关键词长度在1-100字符之间，不包含特殊字符
            2. **AI服务不可用**: 请稍后重试，或联系管理员检查API配置
            3. **分析失败**: 尝试更换关键词，或使用更具体的产品类别
            4. **系统配置错误**: 请联系系统管理员检查配置文件
            
            如问题持续，请联系技术支持。
            """)
