#!/usr/bin/env python3
"""
Phase 3b: Advanced UI Features (90 min)
Day 3 - Advanced Copilot features: Dashboard, analytics, and monitoring

Learning Objectives:
- Advanced Copilot features (Agent Mode, Vision, Edit)
- Hands-on: testing, refactoring, documentation, onboarding
- Building dashboards with real-time analytics
- Advanced monitoring and visualization

This module focuses on advanced UI patterns including dashboards,
analytics visualization, real-time monitoring, and administrative interfaces.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

# Import previous phase capabilities
import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from phase1d_basic_rag import BasicRAGSystem
    from phase2a_simple_agent import SimpleAgent
    from phase2d_mcp_client import MCPEnabledAgent
    from phase3a_basic_ui import CustomerServiceApp, is_streamlit
    RAG_AVAILABLE = True
    AGENT_AVAILABLE = True
    MCP_AVAILABLE = True
    BASIC_UI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    RAG_AVAILABLE = False
    AGENT_AVAILABLE = False
    MCP_AVAILABLE = False
    BASIC_UI_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("advanced-ui")

class AdvancedDashboard:
    """
    Advanced dashboard with analytics, monitoring, and administrative features.
    Demonstrates enterprise-grade UI patterns for AI applications.
    """
    
    def __init__(self):
        """Initialize the advanced dashboard."""
        self.dashboard_name = "AI Enterprise Dashboard"
        self.version = "3.0-Advanced"
        
        # Generate mock analytics data
        self.analytics_data = self._generate_analytics_data()
        self.real_time_metrics = self._generate_real_time_metrics()
        
        # Dashboard configuration
        self.refresh_interval = 5  # seconds
        self.chart_themes = ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn"]
        
    def _generate_analytics_data(self) -> Dict[str, Any]:
        """Generate mock analytics data for demonstration."""
        # Date range for analytics
        days = 30
        dates = [datetime.now() - timedelta(days=x) for x in range(days)]
        dates.reverse()
        
        # Customer interactions
        np.random.seed(42)  # For reproducible demo data
        daily_interactions = np.random.poisson(50, days) + np.random.normal(0, 5, days)
        daily_interactions = np.maximum(daily_interactions, 0)
        
        # Response times
        response_times = np.random.exponential(2.5, days) + np.random.normal(0, 0.5, days)
        response_times = np.maximum(response_times, 0.1)
        
        # Satisfaction scores
        satisfaction = np.random.beta(8, 2, days) * 5  # Beta distribution for realistic satisfaction
        
        # Resolution rates
        resolution_rates = np.random.beta(7, 2, days) * 100
        
        # Agent performance
        agents = ['Agent_Alpha', 'Agent_Beta', 'Agent_Gamma', 'Agent_Delta']
        agent_performance = {}
        for agent in agents:
            agent_performance[agent] = {
                'interactions': np.random.poisson(200, 1)[0],
                'avg_response_time': np.random.exponential(2.0, 1)[0],
                'satisfaction': np.random.beta(7, 2, 1)[0] * 5,
                'resolution_rate': np.random.beta(8, 2, 1)[0] * 100
            }
        
        # Issue categories
        categories = {
            'Returns & Refunds': np.random.poisson(20, days),
            'Shipping Issues': np.random.poisson(15, days),
            'Product Support': np.random.poisson(12, days),
            'Account Issues': np.random.poisson(8, days),
            'Billing Questions': np.random.poisson(6, days),
            'General Inquiry': np.random.poisson(10, days)
        }
        
        return {
            'dates': dates,
            'daily_interactions': daily_interactions,
            'response_times': response_times,
            'satisfaction_scores': satisfaction,
            'resolution_rates': resolution_rates,
            'agent_performance': agent_performance,
            'issue_categories': categories
        }
    
    def _generate_real_time_metrics(self) -> Dict[str, Any]:
        """Generate real-time metrics for live monitoring."""
        return {
            'active_conversations': np.random.randint(15, 45),
            'avg_response_time': np.random.exponential(2.0),
            'queue_length': np.random.randint(0, 12),
            'agent_utilization': np.random.beta(6, 2) * 100,
            'system_load': np.random.beta(3, 7) * 100,
            'error_rate': np.random.exponential(0.02),
            'satisfaction_today': np.random.beta(8, 2) * 5,
            'tickets_resolved_today': np.random.poisson(180),
            'revenue_impact': np.random.exponential(5000),
            'customer_retention': np.random.beta(9, 1) * 100
        }

def setup_advanced_config():
    """Configure Streamlit for advanced dashboard."""
    st.set_page_config(
        page_title="AI Enterprise Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': "AI Enterprise Dashboard - Advanced UI Features Training"
        }
    )

def apply_advanced_css():
    """Apply advanced CSS styling for dashboard components."""
    st.markdown("""
    <style>
        /* Dashboard-specific styling */
        .dashboard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        /* Metric cards */
        .metric-card-advanced {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 4px solid #3b82f6;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            margin: 0.5rem 0;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .metric-card-advanced:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        }
        
        .metric-value-large {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1e40af;
            line-height: 1;
        }
        
        .metric-label-advanced {
            color: #64748b;
            font-size: 0.9rem;
            margin-top: 0.5rem;
            font-weight: 500;
        }
        
        .metric-change {
            font-size: 0.8rem;
            margin-top: 0.5rem;
        }
        
        .metric-change.positive {
            color: #10b981;
        }
        
        .metric-change.negative {
            color: #ef4444;
        }
        
        /* Status indicators */
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.025em;
        }
        
        .status-healthy {
            background-color: #d1fae5;
            color: #065f46;
        }
        
        .status-warning {
            background-color: #fef3c7;
            color: #92400e;
        }
        
        .status-critical {
            background-color: #fee2e2;
            color: #991b1b;
        }
        
        /* Real-time indicators */
        .live-indicator {
            display: inline-flex;
            align-items: center;
            color: #10b981;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        .live-dot {
            width: 8px;
            height: 8px;
            background-color: #10b981;
            border-radius: 50%;
            margin-right: 0.5rem;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        /* Data tables */
        .data-table {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        
        /* Chart containers */
        .chart-container {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            margin: 1rem 0;
        }
        
        /* Alert panels */
        .alert-panel {
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-left: 4px solid #ef4444;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        .alert-panel.warning {
            background: #fffbeb;
            border-color: #fed7aa;
            border-left-color: #f59e0b;
        }
        
        .alert-panel.info {
            background: #eff6ff;
            border-color: #bfdbfe;
            border-left-color: #3b82f6;
        }
        
        /* Navigation tabs */
        .nav-tabs {
            border-bottom: 2px solid #e5e7eb;
            margin-bottom: 2rem;
        }
        
        /* Sidebar enhancements */
        .sidebar-advanced {
            background: #f8fafc;
            padding: 1rem;
            border-radius: 12px;
            margin: 0.5rem 0;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display: none;}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f5f9;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
        }
    </style>
    """, unsafe_allow_html=True)

def initialize_advanced_session_state():
    """Initialize session state for advanced dashboard."""
    defaults = {
        'dashboard_initialized': False,
        'current_tab': 'Overview',
        'auto_refresh': True,
        'chart_theme': 'plotly_white',
        'time_range': '7d',
        'selected_agents': [],
        'alert_level': 'all',
        'real_time_data': [],
        'dashboard_config': {
            'show_predictions': True,
            'enable_alerts': True,
            'chart_animations': True,
            'data_refresh_rate': 5
        }
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def render_dashboard_header():
    """Render advanced dashboard header with live status."""
    st.markdown("""
    <div class="dashboard-header">
        <h1>📊 AI Enterprise Dashboard</h1>
        <p>Advanced Analytics & Monitoring • Real-time Insights • Phase 3b Training</p>
        <div class="live-indicator">
            <div class="live-dot"></div>
            Live Dashboard • Last updated: """ + datetime.now().strftime("%H:%M:%S") + """
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_advanced_sidebar():
    """Render advanced sidebar with dashboard controls."""
    with st.sidebar:
        st.title("🎛️ Dashboard Controls")
        
        # Navigation
        st.markdown('<div class="sidebar-advanced">', unsafe_allow_html=True)
        st.subheader("📑 Navigation")
        
        tabs = ["Overview", "Analytics", "Agents", "System", "Alerts", "Settings"]
        st.session_state.current_tab = st.radio(
            "Select View:",
            tabs,
            index=tabs.index(st.session_state.current_tab)
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Time Range
        st.markdown('<div class="sidebar-advanced">', unsafe_allow_html=True)
        st.subheader("⏰ Time Range")
        st.session_state.time_range = st.selectbox(
            "Data Range:",
            ["1h", "6h", "24h", "7d", "30d", "90d"],
            index=3
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Real-time Controls
        st.markdown('<div class="sidebar-advanced">', unsafe_allow_html=True)
        st.subheader("🔄 Real-time")
        st.session_state.auto_refresh = st.checkbox("Auto-refresh", value=True)
        
        if st.session_state.auto_refresh:
            refresh_rate = st.slider("Refresh rate (s)", 1, 30, 5)
            st.session_state.dashboard_config['data_refresh_rate'] = refresh_rate
        
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Chart Settings
        st.markdown('<div class="sidebar-advanced">', unsafe_allow_html=True)
        st.subheader("📈 Chart Settings")
        st.session_state.chart_theme = st.selectbox(
            "Theme:",
            ["plotly_white", "plotly_dark", "ggplot2", "seaborn", "plotly"],
            index=0
        )
        
        st.session_state.dashboard_config['chart_animations'] = st.checkbox(
            "Enable animations", 
            value=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Export Options
        st.markdown('<div class="sidebar-advanced">', unsafe_allow_html=True)
        st.subheader("📤 Export")
        
        if st.button("📊 Export Analytics", use_container_width=True):
            st.success("Analytics data exported!")
        
        if st.button("📋 Generate Report", use_container_width=True):
            st.success("Report generated!")
        st.markdown('</div>', unsafe_allow_html=True)

def render_overview_tab(dashboard: AdvancedDashboard):
    """Render overview dashboard with key metrics."""
    st.subheader("📊 System Overview")
    
    # Real-time metrics
    metrics = dashboard.real_time_metrics
    
    # Top row metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card-advanced">
            <div class="metric-value-large">{metrics['active_conversations']:.0f}</div>
            <div class="metric-label-advanced">Active Conversations</div>
            <div class="metric-change positive">+12% from yesterday</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card-advanced">
            <div class="metric-value-large">{metrics['avg_response_time']:.1f}s</div>
            <div class="metric-label-advanced">Avg Response Time</div>
            <div class="metric-change negative">+0.3s from yesterday</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card-advanced">
            <div class="metric-value-large">{metrics['satisfaction_today']:.1f}/5</div>
            <div class="metric-label-advanced">Customer Satisfaction</div>
            <div class="metric-change positive">+0.2 from yesterday</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card-advanced">
            <div class="metric-value-large">{metrics['tickets_resolved_today']:.0f}</div>
            <div class="metric-label-advanced">Tickets Resolved Today</div>
            <div class="metric-change positive">+18% from yesterday</div>
        </div>
        """, unsafe_allow_html=True)
    
    # System status indicators
    st.subheader("🔧 System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        load_status = "healthy" if metrics['system_load'] < 70 else "warning" if metrics['system_load'] < 90 else "critical"
        st.markdown(f"""
        <div class="metric-card-advanced">
            <h4>System Load</h4>
            <div class="metric-value-large">{metrics['system_load']:.1f}%</div>
            <span class="status-badge status-{load_status}">{load_status.title()}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        util_status = "healthy" if metrics['agent_utilization'] < 80 else "warning" if metrics['agent_utilization'] < 95 else "critical"
        st.markdown(f"""
        <div class="metric-card-advanced">
            <h4>Agent Utilization</h4>
            <div class="metric-value-large">{metrics['agent_utilization']:.1f}%</div>
            <span class="status-badge status-{util_status}">{util_status.title()}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        error_status = "healthy" if metrics['error_rate'] < 0.01 else "warning" if metrics['error_rate'] < 0.05 else "critical"
        st.markdown(f"""
        <div class="metric-card-advanced">
            <h4>Error Rate</h4>
            <div class="metric-value-large">{metrics['error_rate']:.2%}</div>
            <span class="status-badge status-{error_status}">{error_status.title()}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📈 Daily Interactions (Last 7 Days)")
        
        # Create sample data for last 7 days
        dates = [datetime.now() - timedelta(days=x) for x in range(6, -1, -1)]
        interactions = dashboard.analytics_data['daily_interactions'][-7:]
        
        fig = px.line(
            x=dates, 
            y=interactions,
            title="Customer Interactions Trend"
        )
        fig.update_layout(
            template=st.session_state.chart_theme,
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("🎯 Resolution Rate by Category")
        
        categories = list(dashboard.analytics_data['issue_categories'].keys())
        resolution_rates = [np.random.beta(7, 2) * 100 for _ in categories]
        
        fig = px.bar(
            x=categories,
            y=resolution_rates,
            title="Resolution Rates by Issue Type"
        )
        fig.update_layout(
            template=st.session_state.chart_theme,
            height=300,
            showlegend=False
        )
        fig.update_xaxis(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def render_analytics_tab(dashboard: AdvancedDashboard):
    """Render detailed analytics with interactive charts."""
    st.subheader("📈 Detailed Analytics")
    
    data = dashboard.analytics_data
    
    # Interactive time series
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("📊 Performance Metrics Over Time")
    
    # Create subplot with secondary y-axis
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Daily Interactions', 'Response Times', 'Satisfaction Scores', 'Resolution Rates'),
        vertical_spacing=0.1
    )
    
    # Daily interactions
    fig.add_trace(
        go.Scatter(x=data['dates'], y=data['daily_interactions'], name='Interactions', line=dict(color='#3b82f6')),
        row=1, col=1
    )
    
    # Response times
    fig.add_trace(
        go.Scatter(x=data['dates'], y=data['response_times'], name='Response Time', line=dict(color='#ef4444')),
        row=1, col=2
    )
    
    # Satisfaction scores
    fig.add_trace(
        go.Scatter(x=data['dates'], y=data['satisfaction_scores'], name='Satisfaction', line=dict(color='#10b981')),
        row=2, col=1
    )
    
    # Resolution rates
    fig.add_trace(
        go.Scatter(x=data['dates'], y=data['resolution_rates'], name='Resolution Rate', line=dict(color='#f59e0b')),
        row=2, col=2
    )
    
    fig.update_layout(
        template=st.session_state.chart_theme,
        height=600,
        showlegend=False,
        title_text="Key Performance Indicators Trends"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Issue category analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("🎯 Issue Categories Distribution")
        
        categories = list(data['issue_categories'].keys())
        totals = [sum(data['issue_categories'][cat]) for cat in categories]
        
        fig = px.pie(
            values=totals,
            names=categories,
            title="Distribution of Support Issues"
        )
        fig.update_layout(
            template=st.session_state.chart_theme,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📅 Issue Trends by Category")
        
        # Create stacked area chart
        fig = go.Figure()
        
        for category in categories:
            fig.add_trace(go.Scatter(
                x=data['dates'],
                y=data['issue_categories'][category],
                mode='lines',
                stackgroup='one',
                name=category
            ))
        
        fig.update_layout(
            template=st.session_state.chart_theme,
            height=400,
            title="Issue Volume Trends by Category",
            xaxis_title="Date",
            yaxis_title="Number of Issues"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Correlation analysis
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("🔗 Performance Correlation Matrix")
    
    # Create correlation matrix
    metrics_df = pd.DataFrame({
        'Daily_Interactions': data['daily_interactions'],
        'Response_Time': data['response_times'],
        'Satisfaction': data['satisfaction_scores'],
        'Resolution_Rate': data['resolution_rates']
    })
    
    correlation_matrix = metrics_df.corr()
    
    fig = px.imshow(
        correlation_matrix,
        title="Correlation Between Key Metrics",
        color_continuous_scale='RdBu',
        aspect='auto'
    )
    fig.update_layout(
        template=st.session_state.chart_theme,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_agents_tab(dashboard: AdvancedDashboard):
    """Render agent performance monitoring."""
    st.subheader("🤖 Agent Performance Dashboard")
    
    agent_data = dashboard.analytics_data['agent_performance']
    
    # Agent performance overview
    st.markdown("### 📊 Agent Performance Overview")
    
    agents = list(agent_data.keys())
    cols = st.columns(len(agents))
    
    for i, (agent_name, metrics) in enumerate(agent_data.items()):
        with cols[i]:
            # Determine performance rating
            score = (
                (metrics['satisfaction'] / 5) * 0.4 +
                (min(metrics['resolution_rate'] / 100, 1)) * 0.3 +
                (max(0, 1 - metrics['avg_response_time'] / 5)) * 0.3
            )
            
            rating = "Excellent" if score > 0.8 else "Good" if score > 0.6 else "Needs Improvement"
            rating_color = "#10b981" if score > 0.8 else "#f59e0b" if score > 0.6 else "#ef4444"
            
            st.markdown(f"""
            <div class="metric-card-advanced">
                <h4>{agent_name.replace('_', ' ')}</h4>
                <div class="metric-value-large" style="color: {rating_color}; font-size: 1.5rem;">{score:.1%}</div>
                <div class="metric-label-advanced">{rating}</div>
                <hr style="margin: 1rem 0; border: none; border-top: 1px solid #e5e7eb;">
                <div style="font-size: 0.8rem; color: #64748b;">
                    <div>Interactions: {metrics['interactions']}</div>
                    <div>Avg Response: {metrics['avg_response_time']:.1f}s</div>
                    <div>Satisfaction: {metrics['satisfaction']:.1f}/5</div>
                    <div>Resolution: {metrics['resolution_rate']:.1f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Detailed agent comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("⚡ Response Time Comparison")
        
        agent_names = [name.replace('_', ' ') for name in agents]
        response_times = [agent_data[agent]['avg_response_time'] for agent in agents]
        
        fig = px.bar(
            x=agent_names,
            y=response_times,
            title="Average Response Time by Agent",
            color=response_times,
            color_continuous_scale='RdYlGn_r'
        )
        fig.update_layout(
            template=st.session_state.chart_theme,
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("😊 Satisfaction Scores")
        
        satisfaction_scores = [agent_data[agent]['satisfaction'] for agent in agents]
        
        fig = px.bar(
            x=agent_names,
            y=satisfaction_scores,
            title="Customer Satisfaction by Agent",
            color=satisfaction_scores,
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(
            template=st.session_state.chart_theme,
            height=400,
            showlegend=False
        )
        fig.update_yaxis(range=[0, 5])
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Agent performance radar chart
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("🎯 Multi-dimensional Agent Comparison")
    
    fig = go.Figure()
    
    metrics_names = ['Response Speed', 'Satisfaction', 'Resolution Rate', 'Interaction Volume']
    
    for agent in agents:
        metrics_values = [
            max(0, 1 - agent_data[agent]['avg_response_time'] / 5) * 100,  # Inverted response time
            agent_data[agent]['satisfaction'] * 20,  # Scale to 100
            agent_data[agent]['resolution_rate'],
            min(agent_data[agent]['interactions'] / 300 * 100, 100)  # Scale interactions
        ]
        
        fig.add_trace(go.Scatterpolar(
            r=metrics_values,
            theta=metrics_names,
            fill='toself',
            name=agent.replace('_', ' ')
        ))
    
    fig.update_layout(
        template=st.session_state.chart_theme,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        height=500,
        title="Agent Performance Radar Chart"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_system_tab(dashboard: AdvancedDashboard):
    """Render system monitoring and health."""
    st.subheader("🖥️ System Monitoring")
    
    metrics = dashboard.real_time_metrics
    
    # System health overview
    st.markdown("### 🏥 System Health")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cpu_usage = metrics['system_load']
        cpu_status = "🟢" if cpu_usage < 70 else "🟡" if cpu_usage < 90 else "🔴"
        st.metric("CPU Usage", f"{cpu_usage:.1f}%", delta=f"{cpu_status}")
    
    with col2:
        memory_usage = np.random.beta(4, 6) * 100
        memory_status = "🟢" if memory_usage < 80 else "🟡" if memory_usage < 95 else "🔴"
        st.metric("Memory Usage", f"{memory_usage:.1f}%", delta=f"{memory_status}")
    
    with col3:
        disk_usage = np.random.beta(3, 7) * 100
        disk_status = "🟢" if disk_usage < 85 else "🟡" if disk_usage < 95 else "🔴"
        st.metric("Disk Usage", f"{disk_usage:.1f}%", delta=f"{disk_status}")
    
    with col4:
        network_latency = np.random.exponential(50)
        network_status = "🟢" if network_latency < 100 else "🟡" if network_latency < 200 else "🔴"
        st.metric("Network Latency", f"{network_latency:.0f}ms", delta=f"{network_status}")
    
    # Real-time system metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📊 Real-time System Load")
        
        # Generate real-time data simulation
        time_points = [datetime.now() - timedelta(minutes=x) for x in range(60, 0, -1)]
        load_data = [np.random.beta(4, 6) * 100 + np.sin(x/10) * 10 for x in range(60)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=time_points,
            y=load_data,
            mode='lines+markers',
            name='System Load',
            line=dict(color='#3b82f6', width=2),
            fill='tonexty'
        ))
        
        fig.add_hline(y=70, line_dash="dash", line_color="orange", annotation_text="Warning Threshold")
        fig.add_hline(y=90, line_dash="dash", line_color="red", annotation_text="Critical Threshold")
        
        fig.update_layout(
            template=st.session_state.chart_theme,
            height=400,
            title="System Load (Last Hour)",
            xaxis_title="Time",
            yaxis_title="Load %"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("🔄 Service Status")
        
        services = {
            'LLM Service': np.random.choice(['Online', 'Degraded'], p=[0.9, 0.1]),
            'RAG System': np.random.choice(['Online', 'Offline'], p=[0.95, 0.05]),
            'Vector DB': np.random.choice(['Online', 'Online'], p=[1.0, 0.0]),
            'MCP Server': np.random.choice(['Online', 'Degraded'], p=[0.85, 0.15]),
            'Cache Layer': np.random.choice(['Online', 'Online'], p=[1.0, 0.0]),
            'API Gateway': np.random.choice(['Online', 'Degraded'], p=[0.92, 0.08])
        }
        
        for service, status in services.items():
            status_icon = "🟢" if status == "Online" else "🟡" if status == "Degraded" else "🔴"
            status_class = "healthy" if status == "Online" else "warning" if status == "Degraded" else "critical"
            
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; margin: 0.25rem 0; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <span style="font-weight: 500;">{service}</span>
                <span class="status-badge status-{status_class}">{status_icon} {status}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Error logs and alerts
    st.markdown("### 📋 Recent System Events")
    
    # Mock system events
    events = [
        {"time": "14:32:15", "level": "INFO", "message": "Agent deployment completed successfully", "service": "Agent Manager"},
        {"time": "14:31:42", "level": "WARN", "message": "High memory usage detected on node-2", "service": "System Monitor"},
        {"time": "14:30:18", "level": "INFO", "message": "Cache invalidation completed", "service": "Cache Layer"},
        {"time": "14:29:03", "level": "ERROR", "message": "Failed to connect to external API (retry 3/3)", "service": "API Gateway"},
        {"time": "14:28:41", "level": "INFO", "message": "Database backup completed", "service": "Vector DB"},
    ]
    
    for event in events:
        level_color = {"INFO": "#3b82f6", "WARN": "#f59e0b", "ERROR": "#ef4444"}[event["level"]]
        level_bg = {"INFO": "#eff6ff", "WARN": "#fffbeb", "ERROR": "#fef2f2"}[event["level"]]
        
        st.markdown(f"""
        <div style="display: flex; padding: 0.75rem; margin: 0.25rem 0; background: {level_bg}; border-radius: 8px; border-left: 4px solid {level_color};">
            <div style="min-width: 80px; font-family: monospace; color: {level_color}; font-weight: bold;">
                {event["time"]}
            </div>
            <div style="min-width: 60px; margin: 0 1rem; padding: 0.125rem 0.5rem; background: {level_color}; color: white; border-radius: 4px; font-size: 0.75rem; text-align: center;">
                {event["level"]}
            </div>
            <div style="flex: 1;">
                <div style="font-weight: 500;">{event["message"]}</div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.25rem;">Service: {event["service"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_alerts_tab(dashboard: AdvancedDashboard):
    """Render alerts and notifications."""
    st.subheader("🚨 Alerts & Notifications")
    
    # Alert summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card-advanced">
            <div class="metric-value-large" style="color: #ef4444;">3</div>
            <div class="metric-label-advanced">Critical Alerts</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card-advanced">
            <div class="metric-value-large" style="color: #f59e0b;">7</div>
            <div class="metric-label-advanced">Warning Alerts</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card-advanced">
            <div class="metric-value-large" style="color: #3b82f6;">12</div>
            <div class="metric-label-advanced">Info Notifications</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Active alerts
    st.markdown("### 🔴 Active Alerts")
    
    alerts = [
        {
            "id": "ALT-001",
            "level": "critical",
            "title": "High Response Time Detected",
            "description": "Average response time has exceeded 5 seconds for the last 10 minutes",
            "service": "Agent Processing",
            "time": "2 minutes ago",
            "actions": ["Scale up agents", "Check system load"]
        },
        {
            "id": "ALT-002", 
            "level": "critical",
            "title": "Database Connection Pool Exhausted",
            "description": "Vector database connection pool is at maximum capacity",
            "service": "Vector Database",
            "time": "5 minutes ago",
            "actions": ["Increase pool size", "Check queries"]
        },
        {
            "id": "ALT-003",
            "level": "warning",
            "title": "Memory Usage Above Threshold",
            "description": "System memory usage has been above 85% for 15 minutes",
            "service": "System Resources",
            "time": "8 minutes ago",
            "actions": ["Clear cache", "Restart services"]
        }
    ]
    
    for alert in alerts:
        level_colors = {
            "critical": {"bg": "#fef2f2", "border": "#ef4444", "text": "#991b1b"},
            "warning": {"bg": "#fffbeb", "border": "#f59e0b", "text": "#92400e"},
            "info": {"bg": "#eff6ff", "border": "#3b82f6", "text": "#1e40af"}
        }
        
        colors = level_colors[alert["level"]]
        
        st.markdown(f"""
        <div style="background: {colors['bg']}; border-left: 4px solid {colors['border']}; padding: 1rem; margin: 1rem 0; border-radius: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                <div>
                    <h4 style="margin: 0; color: {colors['text']};">{alert['title']}</h4>
                    <div style="font-size: 0.8rem; color: #64748b; margin: 0.25rem 0;">
                        {alert['id']} • {alert['service']} • {alert['time']}
                    </div>
                </div>
                <span class="status-badge status-{alert['level']}">{alert['level'].title()}</span>
            </div>
            <p style="margin: 0.5rem 0; color: #374151;">{alert['description']}</p>
            <div style="margin-top: 1rem;">
                <strong style="color: {colors['text']};">Suggested Actions:</strong>
                <ul style="margin: 0.5rem 0; padding-left: 1.5rem; color: #374151;">
                    {"".join(f"<li>{action}</li>" for action in alert['actions'])}
                </ul>
            </div>
            <div style="margin-top: 1rem; display: flex; gap: 0.5rem;">
                <button style="background: {colors['border']}; color: white; border: none; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.8rem;">
                    Acknowledge
                </button>
                <button style="background: #6b7280; color: white; border: none; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.8rem;">
                    Snooze
                </button>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_settings_tab():
    """Render dashboard settings and configuration."""
    st.subheader("⚙️ Dashboard Settings")
    
    # Display settings
    st.markdown("### 🖥️ Display Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        dark_mode = st.checkbox("Dark mode", value=False)
        animations = st.checkbox("Enable animations", value=True)
        auto_refresh = st.checkbox("Auto-refresh data", value=True)
    
    with col2:
        density = st.selectbox("Data density", ["Compact", "Comfortable", "Spacious"], index=1)
        theme = st.selectbox("Chart theme", ["Default", "Dark", "Colorful", "Minimal"], index=0)
    
    # Notification settings
    st.markdown("### 🔔 Notifications")
    
    col1, col2 = st.columns(2)
    
    with col1:
        email_alerts = st.checkbox("Email alerts", value=True)
        browser_notifications = st.checkbox("Browser notifications", value=False)
        slack_integration = st.checkbox("Slack integration", value=False)
    
    with col2:
        alert_threshold = st.selectbox("Alert threshold", ["Low", "Medium", "High"], index=1)
        quiet_hours = st.checkbox("Enable quiet hours", value=False)
    
    # Data settings
    st.markdown("### 📊 Data Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        retention_period = st.selectbox("Data retention", ["7 days", "30 days", "90 days", "1 year"], index=2)
        backup_frequency = st.selectbox("Backup frequency", ["Daily", "Weekly", "Monthly"], index=0)
    
    with col2:
        export_format = st.selectbox("Default export format", ["CSV", "JSON", "Excel", "PDF"], index=0)
        timezone = st.selectbox("Timezone", ["UTC", "EST", "PST", "GMT"], index=1)
    
    # Save settings
    if st.button("💾 Save Settings", use_container_width=True):
        st.success("Settings saved successfully!")
    
    if st.button("🔄 Reset to Defaults", use_container_width=True):
        st.warning("Settings reset to default values.")

def main():
    """Main Streamlit application for advanced dashboard."""
    if not is_streamlit():
        print("This module is designed to run with Streamlit.")
        print("Run: streamlit run phase3b_advanced_ui.py")
        return
    
    # Setup
    setup_advanced_config()
    apply_advanced_css()
    initialize_advanced_session_state()
    
    # Initialize dashboard
    if not st.session_state.dashboard_initialized:
        dashboard = AdvancedDashboard()
        st.session_state.dashboard = dashboard
        st.session_state.dashboard_initialized = True
    else:
        dashboard = st.session_state.dashboard
    
    # Auto-refresh logic
    if st.session_state.auto_refresh:
        time.sleep(st.session_state.dashboard_config['data_refresh_rate'])
        dashboard.real_time_metrics = dashboard._generate_real_time_metrics()
        st.rerun()
    
    # Render header
    render_dashboard_header()
    
    # Render sidebar
    render_advanced_sidebar()
    
    # Render main content based on selected tab
    tab = st.session_state.current_tab
    
    if tab == "Overview":
        render_overview_tab(dashboard)
    elif tab == "Analytics":
        render_analytics_tab(dashboard)
    elif tab == "Agents":
        render_agents_tab(dashboard)
    elif tab == "System":
        render_system_tab(dashboard)
    elif tab == "Alerts":
        render_alerts_tab(dashboard)
    elif tab == "Settings":
        render_settings_tab()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; opacity: 0.7; margin: 2rem 0;">
        🎓 <strong>Phase 3b Complete:</strong> Advanced UI Features<br>
        Enterprise Dashboard • Real-time Analytics • Next: Integration & RAG Enhancement
    </div>
    """, unsafe_allow_html=True)

def demo_advanced_ui():
    """
    Demonstrate advanced UI components (non-Streamlit version).
    """
    print("=== Phase 3b: Advanced UI Features Demo ===\n")
    
    dashboard = AdvancedDashboard()
    
    print(f"📊 Dashboard: {dashboard.dashboard_name} v{dashboard.version}")
    print(f"🎨 Chart Themes: {len(dashboard.chart_themes)} available")
    
    # Demo advanced features
    print(f"\n🚀 Advanced Features Demonstrated:")
    features = [
        "Real-time dashboard with live data updates",
        "Interactive analytics with Plotly charts",
        "Multi-dimensional agent performance monitoring",
        "System health monitoring with alerts",
        "Advanced data visualization (correlation, trends)",
        "Responsive design with custom CSS styling",
        "Alert management and notification system",
        "Configurable settings and preferences",
        "Export capabilities and reporting tools",
        "Enterprise-grade monitoring interfaces"
    ]
    
    for feature in features:
        print(f"  • {feature}")
    
    # Analytics summary
    print(f"\n📈 Analytics Data Summary:")
    data = dashboard.analytics_data
    print(f"  • Date range: {len(data['dates'])} days")
    print(f"  • Avg daily interactions: {np.mean(data['daily_interactions']):.1f}")
    print(f"  • Avg response time: {np.mean(data['response_times']):.1f}s")
    print(f"  • Avg satisfaction: {np.mean(data['satisfaction_scores']):.1f}/5")
    print(f"  • Agents tracked: {len(data['agent_performance'])}")
    print(f"  • Issue categories: {len(data['issue_categories'])}")
    
    # Real-time metrics
    print(f"\n⏱️ Current Real-time Metrics:")
    metrics = dashboard.real_time_metrics
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  • {key.replace('_', ' ').title()}: {value:.1f}")
        else:
            print(f"  • {key.replace('_', ' ').title()}: {value}")
    
    # UI Architecture
    print(f"\n🏗️ Advanced UI Architecture:")
    components = [
        "Multi-tab navigation with state management",
        "Real-time data visualization with Plotly",
        "Responsive grid layouts and flexbox design",
        "Custom CSS with animations and transitions",
        "Interactive charts with hover and zoom",
        "Alert system with severity levels",
        "Configurable dashboards and preferences",
        "Export and reporting functionality"
    ]
    
    for component in components:
        print(f"  • {component}")

if __name__ == "__main__":
    if is_streamlit():
        main()
    else:
        demo_advanced_ui()
        print(f"\n🚀 To run the interactive advanced dashboard:")
        print(f"   streamlit run {__file__}")
        print(f"\n🎓 Phase 3b Complete!")
        print(f"Next: Phase 3c - Integration & RAG Enhancement")