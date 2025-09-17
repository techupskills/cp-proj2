#!/usr/bin/env python3
"""
MCP-Enabled Enterprise AI Support Platform
Shows real MCP client-server communication for training
"""

import sys
import os
import warnings
import time

# Suppress warnings
warnings.filterwarnings("ignore")
os.environ['PYTHONWARNINGS'] = 'ignore'

import logging
logging.getLogger().setLevel(logging.ERROR)

# Version marker to force reload
APP_VERSION = "v2.1-with-rag-dashboard"

try:
    import streamlit as st
    import requests
    import pandas as pd
    from datetime import datetime
    import json
    from mcp_agent import CustomerSupportAgent
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install requirements: pip install streamlit requests chromadb pandas mcp")
    sys.exit(1)

# If running with python directly, start streamlit
if __name__ == "__main__" and "streamlit" not in sys.modules:
    import subprocess
    subprocess.run([sys.executable, "-m", "streamlit", "run", __file__])
    sys.exit(0)

# Page config
st.set_page_config(
    page_title="MCP Enterprise AI Platform",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize interface mode
if 'interface_mode' not in st.session_state:
    st.session_state.interface_mode = "Customer View"

# Display version
st.sidebar.write(f"App Version: {APP_VERSION}")

# Enhanced Professional CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Professional Header */
    .main-header {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #60a5fa 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2.5rem;
        text-align: center;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="white" opacity="0.05"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.6;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.025em;
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    /* Professional Sidebar */
    .css-1d391kg {
        background: white;
        border-right: 1px solid #e2e8f0;
        box-shadow: 4px 0 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .sidebar-content {
        padding: 1.5rem;
    }
    
    /* Navigation Cards */
    .nav-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .nav-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px -3px rgba(0, 0, 0, 0.1);
        border-color: #3b82f6;
    }
    
    .nav-card h3 {
        color: #1e293b;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
    }
    
    .nav-card p {
        color: #64748b;
        font-size: 0.875rem;
        margin: 0;
        line-height: 1.4;
    }
    
    /* Enhanced Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 2rem 1.5rem;
        margin: 0.75rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #60a5fa);
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card h3 {
        color: #64748b;
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 0 0 0.75rem 0;
    }
    
    .metric-card h2 {
        color: #1e293b;
        font-size: 2.25rem;
        font-weight: 700;
        margin: 0;
        line-height: 1;
    }
    
    /* Professional Chat Interface */
    .chat-container {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
    }
    
    .chat-message {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #f1f5f9;
        transition: all 0.2s ease;
    }
    
    .chat-message:hover {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .agent-message {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-left: 4px solid #3b82f6;
        border-color: #bfdbfe;
    }
    
    .customer-message {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-left: 4px solid #10b981;
        border-color: #bbf7d0;
    }
    
    .chat-message strong {
        color: #1e293b;
        font-weight: 600;
    }
    
    .chat-timestamp {
        color: #64748b;
        font-size: 0.75rem;
        font-weight: 500;
        opacity: 0.8;
    }
    
    /* Enhanced Forms */
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 1rem !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        outline: none !important;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        color: white !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 15px -3px rgba(0, 0, 0, 0.2) !important;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    }
    
    /* Professional Components */
    .rag-document {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 1px solid #bae6fd;
        border-left: 4px solid #0ea5e9;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .pipeline-step {
        background: white;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #3b82f6;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.2s ease;
    }
    
    .pipeline-step:hover {
        border-left-color: #2563eb;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .pipeline-step h4 {
        color: #1e293b;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0 0 1rem 0;
    }
    
    .rag-analysis {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    /* MCP Protocol Styling */
    .mcp-call {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 1px solid #e2e8f0;
        border-left: 4px solid #3b82f6;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        font-family: 'Inter', monospace;
        transition: all 0.2s ease;
    }
    
    .mcp-success { 
        border-left-color: #10b981;
        background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
    }
    
    .mcp-error { 
        border-left-color: #ef4444;
        background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%);
    }
    
    /* Status Indicators */
    .status-indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .status-healthy { 
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
    }
    
    .status-warning { 
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2);
    }
    
    .status-error { 
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
    }
    
    /* Professional Tables and Lists */
    .professional-table {
        background: white;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        overflow: hidden;
        box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .table-header {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1rem 1.5rem;
        border-bottom: 1px solid #e2e8f0;
        font-weight: 600;
        color: #374151;
    }
    
    .table-row {
        padding: 1rem 1.5rem;
        border-bottom: 1px solid #f1f5f9;
        transition: background-color 0.2s ease;
    }
    
    .table-row:hover {
        background-color: #f8fafc;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            padding: 1.5rem 1rem;
        }
        
        .main-header h1 {
            font-size: 2rem;
        }
        
        .metric-card {
            padding: 1.5rem 1rem;
        }
        
        .chat-container {
            padding: 1.5rem;
        }
    }
    
    /* Custom Scrollbars */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%);
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #94a3b8 0%, #64748b 100%);
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Add admin floating button styles
st.markdown("""
<style>
.admin-floating-button {
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    cursor: pointer;
    box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
    z-index: 9999;
    transition: all 0.3s ease;
    border: none;
}

.admin-floating-button:hover {
    transform: scale(1.1);
    box-shadow: 0 12px 25px rgba(59, 130, 246, 0.6);
}
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    defaults = {
        'interface_mode': "Customer View",
        'conversation_history': [],
        'current_conversation': [],
        'agent_metrics': {
            'total_queries': 0,
            'resolved_queries': 0,
            'tickets_created': 0
        },
        'mcp_logs': [],
        'customer_email': 'john.doe@email.com',
        'agent_initialized': False,
        'agent': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

@st.cache_resource
def initialize_agent():
    """Initialize the MCP agent (cached to prevent reinitialization)"""
    try:
        agent = CustomerSupportAgent()
        return agent
    except Exception as e:
        st.error(f"Failed to initialize MCP agent: {e}")
        return None

def render_header():
    """Render professional main header with enhanced branding"""
    st.markdown("""
    <div class="main-header">
        <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 1rem;">
            <div style="font-size: 3rem;">🔗</div>
            <div style="text-align: left;">
                <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700; letter-spacing: -0.025em;">MCP Enterprise AI Platform</h1>
                <div style="display: flex; align-items: center; gap: 1rem; margin-top: 0.5rem;">
                    <span style="padding: 0.25rem 0.75rem; background: rgba(255,255,255,0.2); border-radius: 20px; font-size: 0.875rem; font-weight: 500;">RAG Enabled</span>
                    <span style="padding: 0.25rem 0.75rem; background: rgba(255,255,255,0.2); border-radius: 20px; font-size: 0.875rem; font-weight: 500;">Real-time Processing</span>
                    <span style="padding: 0.25rem 0.75rem; background: rgba(255,255,255,0.2); border-radius: 20px; font-size: 0.875rem; font-weight: 500;">MCP Protocol</span>
                </div>
            </div>
        </div>
        <p style="margin: 0; font-size: 1.1rem; opacity: 0.9; font-weight: 400; max-width: 600px; margin: 0 auto; line-height: 1.5;">
            Advanced customer support powered by Model Context Protocol, Retrieval-Augmented Generation, and real-time AI processing
        </p>
    </div>
    """, unsafe_allow_html=True)
    

def render_sidebar():
    """Render professional sidebar with enhanced controls and metrics"""
    # Professional sidebar header
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1.5rem 0 2rem 0; border-bottom: 1px solid #e2e8f0; margin-bottom: 2rem;">
        <h2 style="margin: 0; color: #1e293b; font-size: 1.25rem; font-weight: 600;">🎛️ Control Center</h2>
        <p style="margin: 0.5rem 0 0 0; color: #64748b; font-size: 0.875rem;">Manage your AI support experience</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation Cards
    st.sidebar.markdown("### 🧭 Navigation")
    
    # Create navigation options with descriptions
    nav_options = {
        "Customer View": {"icon": "💬", "desc": "Interactive chat interface"},
        "Agent Dashboard": {"icon": "🤖", "desc": "Analytics and RAG insights"}, 
        "MCP Protocol Monitor": {"icon": "🔗", "desc": "Technical monitoring"}
    }
    
    for option, details in nav_options.items():
        is_selected = st.session_state.get('interface_mode', 'Customer View') == option
        card_style = """
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); 
        color: white; 
        border: 2px solid #3b82f6;
        """ if is_selected else """
        background: white; 
        border: 1px solid #e2e8f0;
        """
        
        if st.sidebar.button(
            f"{details['icon']} {option}",
            key=f"nav_{option}",
            help=details['desc'],
            use_container_width=True
        ):
            st.session_state.interface_mode = option
            st.rerun()
        
        if is_selected:
            st.sidebar.markdown(f"<small style='color: #64748b; margin-left: 0.5rem;'>📍 Currently viewing</small>", unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Customer Context Section
    st.sidebar.markdown("### 👤 Customer Context")
    
    customer_options = {
        "john.doe@email.com": {"name": "John Doe", "tier": "Premium", "icon": "👔"},
        "sarah.smith@email.com": {"name": "Sarah Smith", "tier": "Standard", "icon": "👩"},
        "new.customer@email.com": {"name": "New Customer", "tier": "Guest", "icon": "✨"}
    }
    
    # Custom customer selector with enhanced display
    # Get current customer email from session state or default
    current_customer = st.session_state.get('customer_email', 'john.doe@email.com')
    
    # Get index of current customer for selectbox
    customer_keys = list(customer_options.keys())
    try:
        current_index = customer_keys.index(current_customer)
    except ValueError:
        current_index = 0
        current_customer = customer_keys[0]
    
    selected_customer = st.sidebar.selectbox(
        "Select Customer Profile",
        customer_keys,
        index=current_index,
        format_func=lambda x: f"{customer_options[x]['icon']} {customer_options[x]['name']} ({customer_options[x]['tier']})",
        key="customer_email_selector"
    )
    
    # Update session state only if customer changed
    if selected_customer != st.session_state.get('customer_email'):
        st.session_state.customer_email = selected_customer
    
    # Display selected customer info
    customer_info = customer_options[selected_customer]
    st.sidebar.markdown(f"""
    <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.5rem;">{customer_info['icon']}</span>
            <div>
                <div style="font-weight: 600; color: #1e293b;">{customer_info['name']}</div>
                <div style="font-size: 0.75rem; color: #64748b;">{customer_info['tier']} Customer</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # System Performance Metrics
    st.sidebar.markdown("### 📊 Performance Metrics")
    
    metrics = st.session_state.agent_metrics
    
    # Enhanced metrics display
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        st.metric(
            label="Total Queries",
            value=metrics['total_queries'],
            delta=f"+{metrics['total_queries'] - metrics['resolved_queries']}" if metrics['total_queries'] > 0 else None
        )
        
        st.metric(
            label="Tickets Created", 
            value=metrics['tickets_created'],
            delta="+1" if metrics['tickets_created'] > 0 else None
        )
    
    with col2:
        st.metric(
            label="Resolved",
            value=metrics['resolved_queries'],
            delta=f"{(metrics['resolved_queries']/max(metrics['total_queries'],1)*100):.0f}%" if metrics['total_queries'] > 0 else "0%"
        )
        
        # Success rate
        success_rate = (metrics['resolved_queries'] / max(metrics['total_queries'], 1)) * 100
        st.metric(
            label="Success Rate",
            value=f"{success_rate:.0f}%",
            delta="Excellent" if success_rate > 80 else "Good" if success_rate > 60 else "Improving"
        )
    
    st.sidebar.markdown("---")
    
    # System Status
    st.sidebar.markdown("### 🔗 System Status")
    
    # Agent status with enhanced display
    if st.session_state.agent:
        st.sidebar.markdown("""
        <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem; background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); border-radius: 8px; margin: 0.5rem 0;">
            <div class="status-indicator status-healthy"></div>
            <div>
                <div style="font-weight: 600; color: #059669;">MCP Agent Online</div>
                <div style="font-size: 0.75rem; color: #64748b;">All systems operational</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.sidebar.button("🔄 Refresh Stats", use_container_width=True):
            get_mcp_stats()
    else:
        st.sidebar.markdown("""
        <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem; background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%); border-radius: 8px; margin: 0.5rem 0;">
            <div class="status-indicator status-error"></div>
            <div>
                <div style="font-weight: 600; color: #dc2626;">MCP Agent Offline</div>
                <div style="font-size: 0.75rem; color: #64748b;">Connection needed</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.sidebar.button("🔌 Reconnect Agent", use_container_width=True, type="primary"):
            st.session_state.agent = initialize_agent()
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # Advanced Controls
    st.sidebar.markdown("### ⚙️ Advanced Controls")
    
    # Debug mode with better styling
    debug_enabled = st.sidebar.checkbox(
        "🔧 Enable Debug Mode", 
        value=st.session_state.get('debug_mode', False),
        help="Show detailed technical information and logs"
    )
    st.session_state.debug_mode = debug_enabled
    
    # Action buttons
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🗑️ Clear", use_container_width=True, help="Clear conversation history"):
            st.session_state.current_conversation = []
            st.rerun()
    
    with col2:
        if st.button("📊 Stats", use_container_width=True, help="Refresh all statistics"):
            get_mcp_stats()
            st.rerun()
    
    # Quick Actions
    st.sidebar.markdown("### ⚡ Quick Actions")
    
    # Quick Actions with actual functionality
    if st.sidebar.button("💬 New Chat", help="Start a fresh conversation", use_container_width=True):
        st.session_state.current_conversation = []
        st.session_state.agent_metrics = {
            'total_queries': 0,
            'resolved_queries': 0,
            'tickets_created': 0
        }
        st.sidebar.success("✅ New conversation started!")
        st.rerun()
    
    if st.sidebar.button("📁 Export Data", help="Export conversation history as JSON", use_container_width=True):
        if st.session_state.current_conversation:
            import json
            from datetime import datetime
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "customer_email": st.session_state.get('customer_email', 'unknown'),
                "conversation_count": len(st.session_state.current_conversation),
                "metrics": st.session_state.agent_metrics,
                "conversation_history": st.session_state.current_conversation
            }
            
            # Create downloadable JSON
            st.sidebar.download_button(
                label="⬇️ Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name=f"conversation_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        else:
            st.sidebar.warning("No conversation data to export")
    
    # Test Mode toggle
    test_mode_enabled = st.sidebar.checkbox(
        "🎯 Test Mode", 
        value=st.session_state.get('test_mode', False),
        help="Enable mock responses and testing features"
    )
    if test_mode_enabled != st.session_state.get('test_mode', False):
        st.session_state.test_mode = test_mode_enabled
        if test_mode_enabled:
            st.sidebar.success("✅ Test mode enabled - AI responses will use mock data")
        else:
            st.sidebar.info("Test mode disabled - Normal AI responses")
    
    st.sidebar.markdown("---")
    
    # Footer info
    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 1rem 0; color: #64748b; font-size: 0.75rem;">
        <div style="margin-bottom: 0.5rem;">
            <strong>App Version:</strong> {APP_VERSION}
        </div>
        <div>
            🚀 AI Enterprise Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

def get_mcp_stats():
    """Get MCP server statistics"""
    if st.session_state.agent:
        try:
            stats = st.session_state.agent.get_mcp_stats()
            
            # Update the session state with fresh logs
            fresh_logs = st.session_state.agent.get_mcp_call_log()
            st.session_state.mcp_logs = fresh_logs
            
            return stats
        except Exception as e:
            st.error(f"Failed to get MCP stats: {e}")
            return None
    return None

def render_customer_view():
    """Render customer support interface with professional styling"""
    # Customer email input (moved to top for better workflow)
    customer_email = st.text_input(
        "👤 Customer Email:",
        value=st.session_state.get('customer_email', 'john.doe@email.com'),
        placeholder="Enter customer email address...",
        help="Enter the customer's email address and press Enter to load their context",
        key="customer_email_input"
    )
    
    # Update customer email if changed
    if customer_email != st.session_state.get('customer_email'):
        st.session_state.customer_email = customer_email
        st.success(f"✅ Switched to {customer_email}")
    
    st.markdown("---")
    
    # Chat header section
    st.markdown("""
    <div class="chat-container">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid #e2e8f0;">
            <div>
                <h2 style="margin: 0; color: #1e293b; font-size: 1.5rem; font-weight: 600;">Customer Support Chat</h2>
                <p style="margin: 0.5rem 0 0 0; color: #64748b; font-size: 0.95rem;">Get instant help from our AI-powered support assistant</p>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div class="status-indicator status-healthy"></div>
                <span style="color: #059669; font-weight: 500; font-size: 0.875rem;">Online</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display conversation history (only if there are messages)
    if st.session_state.current_conversation:
        for i, message in enumerate(st.session_state.current_conversation):
            if message['sender'] == 'customer':
                st.markdown(f"""
                <div class="chat-container" style="margin-top: 1rem;">
                    <div class="chat-message customer-message" style="margin-left: 2rem;">
                        <div style="display: flex; align-items: start; gap: 0.75rem;">
                            <div style="flex-shrink: 0; width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #10b981, #059669); display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 0.875rem;">You</div>
                            <div style="flex: 1;">
                                <div style="margin-bottom: 0.5rem;">
                                    <span style="color: #1e293b; font-weight: 600;">You</span>
                                    <span class="chat-timestamp" style="margin-left: 0.5rem;">{message['timestamp']}</span>
                                </div>
                                <div style="color: #374151; line-height: 1.5;">{message['content']}</div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-container" style="margin-top: 1rem;">
                    <div class="chat-message agent-message">
                        <div style="display: flex; align-items: start; gap: 0.75rem;">
                            <div style="flex-shrink: 0; width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #3b82f6, #2563eb); display: flex; align-items: center; justify-content: center; color: white; font-size: 1rem;">🤖</div>
                            <div style="flex: 1;">
                                <div style="margin-bottom: 0.5rem;">
                                    <span style="color: #1e293b; font-weight: 600;">AI Support Agent</span>
                                    <span class="chat-timestamp" style="margin-left: 0.5rem;">{message['timestamp']}</span>
                                </div>
                                <div style="color: #374151; line-height: 1.6;">{message['content']}</div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Input form section - always visible and prominent
    if not st.session_state.current_conversation:
        st.markdown("""
        <div class="chat-container" style="margin-top: 1.5rem;">
            <h4 style="margin: 0 0 1rem 0; color: #1e293b; font-size: 1.2rem; font-weight: 600;">How can I help you today?</h4>
            <p style="margin: 0 0 1.5rem 0; color: #64748b; font-size: 0.95rem;">I'm here to assist with any questions about products, orders, returns, shipping, or account issues.</p>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.75rem; margin-bottom: 1.5rem;">
                <div style="padding: 0.75rem; background: #f0f9ff; border-radius: 6px; border-left: 3px solid #3b82f6; font-size: 0.875rem;">
                    <strong>Returns & Refunds</strong><br>
                    <small>30-day return policy</small>
                </div>
                <div style="padding: 0.75rem; background: #f0fdf4; border-radius: 6px; border-left: 3px solid #10b981; font-size: 0.875rem;">
                    <strong>Shipping & Delivery</strong><br>
                    <small>Tracking and delivery times</small>
                </div>
                <div style="padding: 0.75rem; background: #fefbf2; border-radius: 6px; border-left: 3px solid #f59e0b; font-size: 0.875rem;">
                    <strong>Account Help</strong><br>
                    <small>Password and settings</small>
                </div>
                <div style="padding: 0.75rem; background: #fef2f2; border-radius: 6px; border-left: 3px solid #ef4444; font-size: 0.875rem;">
                    <strong>Product Information</strong><br>
                    <small>Specs and warranties</small>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="chat-container" style="margin-top: 1.5rem;">
            <h4 style="margin: 0 0 1.5rem 0; color: #1e293b; font-size: 1.2rem; font-weight: 600;">Continue the conversation</h4>
        """, unsafe_allow_html=True)
    
    with st.form("customer_query_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            query = st.text_area(
                "",
                height=80,
                placeholder="Type your question here... (e.g., 'I need to return my headphones', 'When will my order arrive?', 'I forgot my password')",
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
            submit = st.form_submit_button("✈️ Send", use_container_width=True, type="primary")
            
            # Quick action buttons
            col_a, col_b = st.columns(2)
            with col_a:
                if st.form_submit_button("🔄 Returns", use_container_width=True):
                    st.session_state.quick_query = "I need help with returning an item"
            with col_b:
                if st.form_submit_button("🚚 Shipping", use_container_width=True):
                    st.session_state.quick_query = "I have a question about shipping"
        
        # Handle quick queries
        if hasattr(st.session_state, 'quick_query'):
            query = st.session_state.quick_query
            submit = True
            del st.session_state.quick_query
        
        if submit and query and query.strip():
            process_customer_query(query.strip())
    
    # Close the input form container
    st.markdown('</div>', unsafe_allow_html=True)

def generate_test_response(query, customer_email):
    """Generate mock response for testing purposes"""
    import time
    import random
    
    # Simulate processing time
    time.sleep(random.uniform(0.5, 2.0))
    
    # Generate mock response based on query keywords
    query_lower = query.lower()
    
    mock_responses = {
        'return': "TEST MODE: I can help with returns! This is a mock response for testing. In production, this would connect to our real return system.",
        'shipping': "TEST MODE: Mock shipping information. Standard: 3-5 days, Express: 1-2 days. This is test data only.",
        'password': "TEST MODE: For password resets, this would normally connect to our authentication system. This is a test response.",
        'account': "TEST MODE: Account assistance mock response. Real system would access customer database.",
        'product': "TEST MODE: Product information mock response. Would normally query our product catalog.",
        'default': "TEST MODE: This is a mock AI response for testing purposes. The query was processed in test mode."
    }
    
    # Find appropriate response
    response_key = 'default'
    for key in mock_responses.keys():
        if key in query_lower and key != 'default':
            response_key = key
            break
    
    return {
        'response': mock_responses[response_key],
        'confidence': random.uniform(0.7, 0.95),
        'knowledge_sources': random.randint(1, 4),
        'knowledge_categories': ['Test Category'],
        'action_needed': 'none',
        'customer_tier': 'Test Customer',
        'mcp_calls_made': 0,
        'processing_time_ms': random.randint(500, 2000),
        'test_mode': True
    }

def process_customer_query(query):
    """Process customer query through MCP agent"""
    if not st.session_state.agent:
        st.error("Agent not initialized. Please refresh the page.")
        return
    
    # Add customer message to conversation
    customer_msg = {
        'sender': 'customer',
        'content': query,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.current_conversation.append(customer_msg)
    
    # Show processing indicator
    spinner_text = "🧪 Test Mode - Generating mock response..." if st.session_state.get('test_mode', False) else "🤖 AI Agent processing your request..."
    with st.spinner(spinner_text):
        try:
            # Check if test mode is enabled
            if st.session_state.get('test_mode', False):
                # Generate mock response for testing
                result = generate_test_response(query, st.session_state.customer_email)
            else:
                # Process through MCP agent with conversation context
                result = st.session_state.agent.process_customer_inquiry(
                    st.session_state.customer_email, 
                    query,
                    conversation_history=st.session_state.current_conversation
                )
            
            # Debug: Show what we got from the agent
            if st.session_state.get('debug_mode', False):
                st.write("🔧 Debug - Agent Result Keys:", list(result.keys()))
                st.write("🔧 Debug - Retrieved Documents:", len(result.get('retrieved_documents', [])))
                if result.get('retrieved_documents'):
                    st.write("🔧 Debug - First doc sample:", result['retrieved_documents'][0])
            
            # Add agent response to conversation with enhanced metadata
            response_content = result.get('response', 'I apologize, but I encountered an error processing your request.')
            
            # Ensure response content is clean text, not JSON
            if isinstance(response_content, dict):
                response_content = response_content.get('response', str(response_content))
            elif isinstance(response_content, str) and response_content.startswith('{'):
                try:
                    parsed = json.loads(response_content)
                    response_content = parsed.get('response', response_content)
                except:
                    pass  # Keep original if parsing fails
            
            agent_msg = {
                'sender': 'agent',
                'content': response_content,
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'confidence': result.get('confidence', 0),
                'knowledge_sources': result.get('knowledge_sources', 0),
                'knowledge_categories': result.get('knowledge_categories', []),
                'action_needed': result.get('action_needed', 'none'),
                'customer_tier': result.get('customer_tier', 'Unknown'),
                'mcp_calls_made': result.get('mcp_calls_made', 0),
                'processing_time_ms': result.get('processing_time_ms', 0),
                'rag_documents_used': result.get('knowledge_categories', []),  # Store for dashboard
                'retrieved_documents': result.get('retrieved_documents', []),  # Full document details
                'search_query': result.get('search_query', ''),
                'document_retrieval_summary': result.get('document_retrieval_summary', {}),
                'llm_prompt': result.get('llm_prompt', '')  # Store the actual LLM prompt
            }
            st.session_state.current_conversation.append(agent_msg)
            
            # Update metrics
            st.session_state.agent_metrics['total_queries'] += 1
            if result.get('confidence', 0) > 0.7:
                st.session_state.agent_metrics['resolved_queries'] += 1
            if result.get('action_needed') == 'create_ticket':
                st.session_state.agent_metrics['tickets_created'] += 1
            
            # Show ticket creation if needed
            if 'ticket_created' in result:
                ticket_info = result['ticket_created']
                if isinstance(ticket_info, dict) and 'id' in ticket_info:
                    st.success(f"🎫 Support ticket created: {ticket_info['id']}")
                else:
                    st.success("🎫 Support ticket created successfully")
            
        except Exception as e:
            st.error(f"Error processing query: {e}")
            # Add error message to conversation
            error_msg = {
                'sender': 'agent',
                'content': 'I apologize, but I encountered a technical error. Please try again.',
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'confidence': 0,
                'knowledge_sources': 0,
                'error': str(e)
            }
            st.session_state.current_conversation.append(error_msg)
    
    st.rerun()

def render_agent_dashboard():
    """Render professional agent dashboard with detailed metrics and RAG information"""
    # Professional dashboard header (without container, just styling)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem; padding: 2rem; background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); border-radius: 16px; border: 1px solid #e2e8f0;">
        <h2 style="margin: 0; color: #1e293b; font-size: 1.75rem; font-weight: 600;">Agent Performance Dashboard</h2>
        <p style="margin: 0.5rem 0 0 0; color: #64748b; font-size: 1rem;">Real-time analytics and RAG pipeline insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced metrics row with better styling
    col1, col2, col3 = st.columns(3)
    
    metrics = st.session_state.agent_metrics
    resolved = metrics['resolved_queries']
    total = metrics['total_queries']
    rate = (resolved / total * 100) if total > 0 else 0
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Queries Processed</h3>
            <h2>{total}</h2>
            <div style="margin-top: 0.5rem; font-size: 0.875rem; color: #64748b;">
                {'+' + str(total - resolved) if total > resolved else '0'} pending
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        rate_color = '#059669' if rate > 80 else '#f59e0b' if rate > 60 else '#ef4444'
        rate_percentage = f"{rate:.1f}"
        st.markdown(f"""
        <div class="metric-card">
            <h3>Resolution Success Rate</h3>
            <h2 style="color: {rate_color};">{rate_percentage}%</h2>
            <div style="margin-top: 0.5rem; font-size: 0.875rem; color: #64748b;">
                {resolved} of {total} resolved
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        escalation_rate = (metrics['tickets_created'] / max(total, 1) * 100) if total > 0 else 0
        escalation_percentage = f"{escalation_rate:.1f}"
        st.markdown(f"""
        <div class="metric-card">
            <h3>Support Tickets Created</h3>
            <h2>{metrics['tickets_created']}</h2>
            <div style="margin-top: 0.5rem; font-size: 0.875rem; color: #64748b;">
                {escalation_percentage}% escalation rate
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # RAG Pipeline Analysis
    st.markdown('<div class="rag-analysis">', unsafe_allow_html=True)
    st.subheader("🔍 RAG Pipeline Analysis")
    
    if st.session_state.current_conversation:
        # Get the most recent conversation entries
        agent_messages = [msg for msg in st.session_state.current_conversation if msg['sender'] == 'agent']
        
        for i, msg in enumerate(agent_messages[-3:]):  # Show last 3 agent responses
            st.markdown(f"""
            <div class="pipeline-step">
                <h4>Agent Response #{len(agent_messages) - 2 + i}</h4>
                <p><strong>Response:</strong> {msg['content'][:200]}{'...' if len(msg['content']) > 200 else ''}</p>
                <p><strong>Confidence:</strong> {msg.get('confidence', 'N/A')} | <strong>Knowledge Sources Used:</strong> {msg.get('knowledge_sources', 0)}</p>
                <p><strong>Customer Tier:</strong> {msg.get('customer_tier', 'Unknown')} | <strong>Processing Time:</strong> {msg.get('processing_time_ms', 'N/A')}ms</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show detailed RAG documents with search visualization
            retrieved_docs = msg.get('retrieved_documents', [])
            if retrieved_docs:
                retrieval_summary = msg.get('document_retrieval_summary', {})
                search_query = msg.get('search_query', 'N/A')
                
                st.markdown(f"**Search Process for: '{search_query}'**")
                st.markdown(f"**📊 Retrieval Summary:** {retrieval_summary.get('total_retrieved', 0)} documents found | Avg Similarity: {retrieval_summary.get('avg_similarity', 0):.3f}")
                
                # Show documents in an expandable section
                with st.expander(f"📚 View Retrieved Knowledge Documents ({len(retrieved_docs)} found)", expanded=False):
                    for j, doc in enumerate(retrieved_docs):
                        similarity_bar = "🟩" * int(doc.get('similarity', 0) * 10) + "⬜" * (10 - int(doc.get('similarity', 0) * 10))
                        similarity_score = f"{doc.get('similarity', 0):.3f}"
                        keywords_joined = ', '.join(doc.get('matched_keywords', []))
                        st.markdown(f"""
                        <div class="rag-document" style="margin: 0.5rem 0; padding: 1rem; background: #f0f9ff; border-left: 4px solid #0ea5e9; border-radius: 8px;">
                            <h4>Document {j+1}: {doc.get('category', 'Unknown').title()} Policy</h4>
                            <p><strong>Content:</strong> {doc.get('content', 'No content available')}</p>
                            <p><strong>Similarity Score:</strong> {similarity_bar} ({similarity_score}) | 
                               <strong>Keywords Matched:</strong> {keywords_joined}
                            </p>
                            <details>
                                <summary>Technical Details</summary>
                                <p><strong>Document ID:</strong> {doc.get('id', 'N/A')}</p>
                                <p><strong>All Keywords:</strong> {', '.join([k.strip() for k in doc.get('keywords', [])])}</p>
                                <p><strong>Distance:</strong> {doc.get('distance', 0)}</p>
                                <p><strong>Relevance Score:</strong> {doc.get('relevance_score', 0)}</p>
                                <p><strong>Retrieval Method:</strong> {doc.get('retrieval_method', 'N/A')}</p>
                                <p><strong>Source:</strong> {doc.get('source', 'Unknown')}</p>
                            </details>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown("**📚 No specific knowledge documents retrieved for this query**")
    else:
        st.info("No conversations yet. Start chatting in Customer View to see RAG pipeline analysis!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent MCP Tool Calls (RAG Operations)
    st.subheader("⚙️ Recent RAG & Tool Operations")
    
    # Get fresh MCP logs
    if st.session_state.agent:
        fresh_logs = st.session_state.agent.get_mcp_call_log()
        
        if fresh_logs:
            # Show last 5 operations
            for log in fresh_logs[-5:]:
                operation_icon = {
                    'search_knowledge_base': '📚',
                    'lookup_customer': '👤', 
                    'create_support_ticket': '🎫',
                    'get_server_stats': '📊'
                }.get(log['tool'], '🔧')
                
                success_indicator = "✅" if log.get('success', False) else "❌"
                
                st.markdown(f"""
                <div class="pipeline-step">
                    <h4>{operation_icon} {log['tool'].replace('_', ' ').title()} {success_indicator}</h4>
                    <p><strong>Time:</strong> {log['timestamp'][:19]} | <strong>Duration:</strong> {log['duration_ms']}ms</p>
                    <p><strong>Arguments:</strong> {json.dumps(log['arguments'], indent=2)}</p>
                    <details>
                        <summary>View Result</summary>
                        <pre style="background: #f8fafc; padding: 0.5rem; border-radius: 4px; font-size: 0.8rem;">
{json.dumps(log['result'], indent=2) if isinstance(log['result'], dict) else str(log['result'])[:500]}
                        </pre>
                    </details>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No MCP operations logged yet.")
    
    # LLM Prompt Analysis - Show actual prompts sent to LLM
    st.subheader("💭 LLM Prompt Engineering Analysis")
    
    if st.session_state.current_conversation:
        # Get agent messages with prompts
        agent_messages = [msg for msg in st.session_state.current_conversation if msg['sender'] == 'agent']
        
        if agent_messages:
            avg_confidence = sum(msg.get('confidence', 0) for msg in agent_messages) / len(agent_messages)
            total_sources = sum(msg.get('knowledge_sources', 0) for msg in agent_messages)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Average Confidence", f"{avg_confidence:.2f}")
                st.metric("Total RAG Retrievals", total_sources)
            
            with col2:
                st.metric("Avg Sources per Query", f"{total_sources/len(agent_messages):.1f}")
                ticket_rate = sum(1 for msg in agent_messages if msg.get('action_needed') == 'create_ticket') / len(agent_messages) * 100
                st.metric("Escalation Rate", f"{ticket_rate:.1f}%")
            
            # Show actual LLM prompts
            st.markdown("**📝 Recent LLM Prompts (with RAG Data)**")
            
            # Display the most recent prompts
            for i, msg in enumerate(agent_messages[-2:]):  # Show last 2 prompts
                if msg.get('llm_prompt'):
                    st.markdown(f"""
                    <div class="pipeline-step">
                        <h4>🔤 LLM Prompt #{len(agent_messages) - 1 + i}</h4>
                        <p><strong>Customer Query:</strong> {msg.get('search_query', 'N/A')}</p>
                        <p><strong>Response Confidence:</strong> {msg.get('confidence', 'N/A')} | <strong>Knowledge Sources:</strong> {msg.get('knowledge_sources', 0)}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show the actual prompt in an expandable section
                    with st.expander(f"📄 View Full LLM Prompt #{len(agent_messages) - 1 + i}", expanded=False):
                        st.markdown("**Complete prompt sent to LLM (including RAG data):**")
                        st.code(msg['llm_prompt'], language="text")
                        
                        # Parse out RAG data section for easier viewing
                        prompt_lines = msg['llm_prompt'].split('\n')
                        rag_section_start = -1
                        rag_section_end = -1
                        
                        for idx, line in enumerate(prompt_lines):
                            if "RELEVANT COMPANY POLICIES & INFORMATION:" in line:
                                rag_section_start = idx + 1
                            elif "CUSTOMER INQUIRY:" in line and rag_section_start > -1:
                                rag_section_end = idx - 1
                                break
                        
                        if rag_section_start > -1 and rag_section_end > -1:
                            rag_content = '\n'.join(prompt_lines[rag_section_start:rag_section_end]).strip()
                            if rag_content:
                                st.markdown("**RAG Knowledge Included in Prompt:**")
                                st.text_area("RAG Data", rag_content, height=200, key=f"rag_{i}_{len(agent_messages)}")
            
            if not any(msg.get('llm_prompt') for msg in agent_messages):
                st.info("No LLM prompts available. This feature requires the updated agent code.")
    
    # Clear conversation button
    if st.button("🗑️ Clear Conversation History"):
        st.session_state.current_conversation = []
        st.rerun()

def render_mcp_monitor():
    """Render MCP protocol monitoring interface"""
    st.subheader("🔗 MCP Protocol Monitor")
    
    # Get fresh stats
    stats = get_mcp_stats()
    
    # Debug: Show what we actually got
    if st.checkbox("Show Debug Info"):
        st.write("Raw stats:", stats)
    
    # Check if we have valid stats
    valid_stats = (
        stats and 
        isinstance(stats, dict) and 
        'server_stats' in stats and 
        isinstance(stats['server_stats'], dict)
    )
    
    if valid_stats:
        server_stats = stats['server_stats']
        
        # Server metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total MCP Requests", server_stats.get('total_requests', 0))
        with col2:
            st.metric("Knowledge Documents", server_stats.get('knowledge_documents', 0))
        with col3:
            st.metric("Customers in DB", server_stats.get('customers_in_db', 0))
        
        # Available tools
        st.subheader("🛠️ Available MCP Tools")
        tools = server_stats.get('tools_available', [])
        for tool in tools:
            st.markdown(f"✅ `{tool}`")
    else:
        # Show error or fallback info
        st.warning("Unable to connect to MCP server")
        
        if stats:
            if isinstance(stats, str):
                st.error(f"MCP returned error: {stats}")
            elif isinstance(stats, dict) and 'error' in stats:
                st.error(f"MCP Error: {stats['error']}")
            elif isinstance(stats, dict) and 'server_stats' in stats:
                if isinstance(stats['server_stats'], str):
                    st.error(f"Server error: {stats['server_stats']}")
        
        # Show basic fallback info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("MCP Status", "Disconnected")
        with col2:
            st.metric("Agent Status", "Active" if st.session_state.agent else "Inactive")
        with col3:
            st.metric("Interface Mode", st.session_state.interface_mode)
    
    # Document Search Analytics
    st.subheader("🔍 Document Search Analytics")
    
    # Debug: Show conversation state
    if st.checkbox("🔧 Debug: Show Conversation Data"):
        st.write("Conversation length:", len(st.session_state.current_conversation))
        for i, msg in enumerate(st.session_state.current_conversation[-3:]):  # Last 3 messages
            st.write(f"Message {i}: sender={msg.get('sender')}, has_retrieved_docs={bool(msg.get('retrieved_documents'))}")
            if msg.get('retrieved_documents'):
                st.write(f"  - Document count: {len(msg['retrieved_documents'])}")
                st.write(f"  - Sample keys: {list(msg.keys())}")
    
    if st.session_state.current_conversation:
        # Get search operations from conversation
        search_operations = []
        for msg in st.session_state.current_conversation:
            if msg['sender'] == 'agent' and msg.get('retrieved_documents'):
                search_operations.append(msg)
        
        if search_operations:
            # Display search analytics
            total_docs_retrieved = sum(len(msg.get('retrieved_documents', [])) for msg in search_operations)
            unique_categories = set()
            all_similarities = []
            
            for msg in search_operations:
                for doc in msg.get('retrieved_documents', []):
                    unique_categories.add(doc.get('category', 'unknown'))
                    all_similarities.append(doc.get('similarity', 0))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Searches", len(search_operations))
            with col2:
                st.metric("Documents Retrieved", total_docs_retrieved)
            with col3:
                avg_sim = sum(all_similarities) / len(all_similarities) if all_similarities else 0
                st.metric("Avg Similarity", f"{avg_sim:.3f}")
            
            # Show category distribution
            st.markdown("**📂 Knowledge Categories Accessed:**")
            for category in unique_categories:
                count = sum(1 for msg in search_operations 
                           for doc in msg.get('retrieved_documents', []) 
                           if doc.get('category') == category)
                st.markdown(f"• {category.title()}: {count} retrievals")
            
        else:
            st.info("No search operations recorded yet. Try asking questions in Customer View!")
    else:
        st.info("No conversation history available for search analytics.")
    
    # Recent MCP calls
    st.subheader("📡 Recent MCP Calls")
    mcp_logs = st.session_state.mcp_logs
    
    if mcp_logs:
        for log in mcp_logs[-10:]:  # Show last 10 calls
            status_class = "mcp-success" if log.get('success', False) else "mcp-error"
            st.markdown(f"""
            <div class="mcp-call {status_class}">
                <strong>🔧 {log['tool']}</strong> ({log['timestamp'][:19]})<br>
                <small>Duration: {log['duration_ms']}ms</small><br>
                <small>Args: {json.dumps(log['arguments'], indent=2)}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No MCP calls logged yet. Try asking a question in Customer View!")
    
    # Auto-refresh toggle
    if st.checkbox("Auto-refresh (5s)"):
        time.sleep(5)
        st.rerun()

def render_admin_popup():
    """Render floating admin button with popup functionality"""
    # Initialize admin popup state
    if 'show_admin_popup' not in st.session_state:
        st.session_state.show_admin_popup = False
    
    # Create the floating admin button with Streamlit button in a fixed container
    # Place it in the main content area with absolute positioning
    with st.container():
        # Create a floating admin button that actually works
        admin_col1, admin_col2 = st.columns([9, 1])
        with admin_col2:
            # Position this button at the bottom right
            st.markdown("""
            <style>
            div[data-testid="column"]:nth-child(2) > div > div > div > button {
                position: fixed !important;
                bottom: 30px !important;
                right: 30px !important;
                z-index: 9999 !important;
                width: 60px !important;
                height: 60px !important;
                border-radius: 50% !important;
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
                border: none !important;
                color: white !important;
                font-size: 24px !important;
                box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4) !important;
                transition: all 0.3s ease !important;
            }
            div[data-testid="column"]:nth-child(2) > div > div > div > button:hover {
                transform: scale(1.1) !important;
                box-shadow: 0 12px 25px rgba(59, 130, 246, 0.6) !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            if st.button("⚙️", key="floating_admin_button", help="Admin Panel - Switch Views"):
                st.session_state.show_admin_popup = not st.session_state.show_admin_popup
                st.rerun()
    
    # Show popup when admin button is clicked
    if st.session_state.show_admin_popup:
        # Simple popup without overlay that blocks clicks
        st.markdown("---")
        
        # Create a prominent popup box
        with st.container():
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                border: 2px solid #3b82f6;
                border-radius: 16px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 10px 25px rgba(59, 130, 246, 0.2);
            ">
            """, unsafe_allow_html=True)
            
            st.markdown("### 🛠️ Admin Panel - Quick View Switcher")
            st.markdown("**Click any button to switch views:**")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💬 Customer View", key="popup_customer", use_container_width=True, type="primary"):
                    st.session_state.interface_mode = "Customer View"
                    st.session_state.show_admin_popup = False
                    st.rerun()
            with col2:
                if st.button("🤖 Agent Dashboard", key="popup_agent", use_container_width=True, type="primary"):
                    st.session_state.interface_mode = "Agent Dashboard"
                    st.session_state.show_admin_popup = False
                    st.rerun()
            with col3:
                if st.button("🔗 MCP Monitor", key="popup_mcp", use_container_width=True, type="primary"):
                    st.session_state.interface_mode = "MCP Protocol Monitor"
                    st.session_state.show_admin_popup = False
                    st.rerun()
            
            st.markdown("**Keyboard Shortcuts:** `Ctrl+1`, `Ctrl+2`, `Ctrl+3`")
            
            if st.button("✖️ Close Admin Panel", key="popup_close", use_container_width=True):
                st.session_state.show_admin_popup = False
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

def main():
    """Main application logic"""
    init_session_state()
    render_header()
    render_sidebar()
    
    # Initialize agent if not done
    if not st.session_state.agent:
        with st.spinner("🚀 Initializing MCP Agent..."):
            st.session_state.agent = initialize_agent()
            if st.session_state.agent:
                st.success("✅ MCP Agent initialized successfully!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Failed to initialize MCP Agent. Please check your setup.")
                st.stop()
    
    # Render admin popup (always available)
    render_admin_popup()
    
    # Render appropriate interface based on mode
    if st.session_state.interface_mode == "Customer View":
        render_customer_view()
    elif st.session_state.interface_mode == "Agent Dashboard":
        render_agent_dashboard()
    elif st.session_state.interface_mode == "MCP Protocol Monitor":
        render_mcp_monitor()

if __name__ == "__main__":
    main()